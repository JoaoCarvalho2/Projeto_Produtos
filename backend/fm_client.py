import os
import requests
import base64
import logging
import json
from datetime import datetime
from typing import List, Dict, Any, Optional

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class FileMakerClient:
    """Cliente para interagir com a API de Dados do FileMaker."""

    def __init__(self):
        self.host = os.getenv("FM_HOST")
        self.database = os.getenv("FM_DATABASE")
        self.user = os.getenv("FM_USER")
        self.password = os.getenv("FM_PASSWORD")
        self.layout_lead = os.getenv("FM_LAYOUT_LEAD")
        self.layout_proposta = os.getenv("FM_LAYOUT_PROPOSTA")
        self.ssl_verify = os.getenv("DISABLE_SSL_VERIFY", "false").lower() != "true"
        if not self.ssl_verify:
            import urllib3
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
            logging.warning("Verificação SSL foi desabilitada. Não recomendado para produção.")
        self.base_url = f"https://{self.host}/fmi/data/vLatest/databases/{self.database}"
        self.token = self._get_token()
        if not self.token:
            raise ConnectionError("Falha crítica na autenticação com o FileMaker. Verifique as credenciais e a conectividade.")

    def _get_token(self) -> Optional[str]:
        auth_str = f"{self.user}:{self.password}"
        auth_b64 = base64.b64encode(auth_str.encode()).decode()
        headers = {"Authorization": f"Basic {auth_b64}", "Content-Type": "application/json"}
        url = f"{self.base_url}/sessions"
        try:
            response = requests.post(url, headers=headers, json={}, verify=self.ssl_verify, timeout=10)
            response.raise_for_status()
            data = response.json()
            if "response" in data and "token" in data["response"]:
                token = data["response"]["token"]
                if token:
                    logging.info(f"Token de sessão FileMaker gerado com SUCESSO.")
                    return token
            return None
        except requests.exceptions.RequestException as e:
            logging.error(f"Erro de conexão CRÍTICO ao autenticar: {e}")
            return None

    def _perform_request(self, method: str, url: str, **kwargs) -> Optional[Dict[str, Any]]:
        if not self.token: return None
        headers = {"Authorization": f"Bearer {self.token}", "Content-Type": "application/json"}
        kwargs['headers'] = headers
        kwargs['verify'] = self.ssl_verify
        try:
            response = requests.request(method, url, **kwargs)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 401:
                logging.warning("Token do FileMaker expirou. Renovando...")
                self.token = self._get_token()
                if self.token: return self._perform_request(method, url, **kwargs)
            logging.error(f"Erro HTTP na requisição: {e.response.status_code} - {e.response.text}")
        return None

    def get_leads_with_proposals(self, date_from: str, date_to: str) -> List[Dict[str, Any]]:
        """Busca leads e anexa a proposta MAIS RECENTE para cada um."""
        logging.info(f"Buscando leads via _find entre {date_from} e {date_to} para o fabricante 'Atlassian'")
        
        try:
            date_from_obj = datetime.strptime(date_from, "%Y-%m-%d")
            date_to_obj = datetime.strptime(date_to, "%Y-%m-%d")
            date_from_fm = date_from_obj.strftime("%m/%d/%Y")
            date_to_fm = date_to_obj.strftime("%m/%d/%Y")
            dates_for_fm = f"{date_from_fm}...{date_to_fm}"
                                                            #seleciona aqui o software(pensando em criar lista baseado nos valores do FM mas n sei fazer.)
            payload = {
                "query": [{"data_criacao": dates_for_fm, "fabricante": "==Atlassian"}],
                "limit": 1000
            }
            
            url = f"{self.base_url}/layouts/{self.layout_lead}/_find"
            response_data = self._perform_request("POST", url, json=payload)

        except Exception as e:
            logging.error(f"Um erro inesperado ocorreu durante a busca de leads: {e}")
            return []

        if not response_data:
            logging.error("Nenhuma resposta do FileMaker ao executar _find.")
            return []

        leads = response_data.get("response", {}).get("data", [])
        if not leads:
            logging.warning("Busca (_find) executada com sucesso, mas nenhum lead encontrado.")
            return []

        logging.info(f"Encontrados {len(leads)} leads. Buscando a proposta mais recente para cada...")
        
        results = []
        for lead in leads:
            lead_data = lead.get("fieldData", {})
            lead_id = lead_data.get("id")
            if not lead_id:
                continue

            # Busca a proposta mais recente
            proposta = self._get_latest_proposal_for_lead(str(lead_id))
            
            # Monta o resultado final com a proposta encontrada (ou com campos vazios se não houver)
            #Tem que criar Issues no Jira como proposta talvez ver com o Rodrigo a necessidade. (Se necessário o payload terá que ser refeito)
            results.append({
                "lead_id": str(lead_id),
                "proposta_id": proposta.get("id") if proposta else None,
                "lead_fields": lead_data,
                "proposta_fields": proposta if proposta else {}
            })

        logging.info(f"Processamento finalizado. {len(results)} resultados gerados.")
        return results

    def _get_latest_proposal_for_lead(self, lead_id: str) -> Optional[Dict[str, Any]]:
        """Busca a proposta mais recente (maior ID) para um lead específico."""
        proposal_link_field = os.getenv("FM_PROPOSAL_LINK_FIELD", "lead.proposta::id")
            
        query = [{proposal_link_field: f"=={lead_id}"}]
        

        find_payload = {
            "query": query, 
            "limit": 1,
            "sort": [
                {"fieldName": "id", "sortOrder": "descend"}
            ]
        }
        url = f"{self.base_url}/layouts/{self.layout_proposta}/_find"
        
        response_data = self._perform_request("POST", url, json=find_payload)
        
        propostas = response_data.get("response", {}).get("data", [])
        if propostas:
            logging.info(f"Proposta mais recente encontrada para o lead ID: {lead_id}")
            return propostas[0].get("fieldData", {})
            
        logging.info(f"Nenhuma proposta encontrada para o lead ID: {lead_id}")
        return None