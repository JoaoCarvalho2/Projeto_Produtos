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
        logging.info(f"Tentando autenticar no FileMaker em {url} com o usuário '{self.user}'")
        try:
            response = requests.post(url, headers=headers, json={}, verify=self.ssl_verify, timeout=10)
            response.raise_for_status()
            data = response.json()
            if "response" in data and "token" in data["response"]:
                token = data["response"]["token"]
                if token:
                    logging.info(f"Token de sessão FileMaker gerado com SUCESSO.")
                    return token
            logging.error(f"Autenticação FALHOU. Resposta 'OK' recebida, mas sem token válido. Resposta: {data}")
            return None
        except requests.exceptions.HTTPError as e:
            logging.error(f"Erro HTTP CRÍTICO ao autenticar: {e.response.status_code} - {e.response.text}")
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
            if e.response.status_code == 500:
                logging.error(f"Erro interno do FileMaker (500): {e.response.text}")
                return e.response.json()
            if e.response.status_code == 401:
                logging.warning("Token do FileMaker expirou. Renovando...")
                self.token = self._get_token()
                if self.token: return self._perform_request(method, url, **kwargs)
            if e.response.status_code in [404, 401]:
                 return e.response.json()
            logging.error(f"Erro HTTP na requisição: {e.response.status_code} - {e.response.text}")
        except requests.exceptions.RequestException as e:
            logging.error(f"Erro de conexão na requisição: {e}")
        return None

    def get_leads_with_proposals(self, date_from: str, date_to: str) -> List[Dict[str, Any]]:
        """
        Busca leads por intervalo de data e fabricante usando o endpoint _find.
        """
        logging.info(f"Buscando leads via _find entre {date_from} e {date_to} para o fabricante 'Atlassian'")
        
        try:
            date_from_obj = datetime.strptime(date_from, "%Y-%m-%d")
            date_to_obj = datetime.strptime(date_to, "%Y-%m-%d")
            date_from_fm = date_from_obj.strftime("%m/%d/%Y")
            date_to_fm = date_to_obj.strftime("%m/%d/%Y")
            dates_for_fm = f"{date_from_fm}...{date_to_fm}"
            
            payload = {
                "query": [{"lead::data_criacao": dates_for_fm, "lead::fabricante": "==Atlassian"}],
                "limit": 100
            }
            
            url = f"{self.base_url}/layouts/{self.layout_lead}/_find"
            logging.info(f"Executando _find com o payload: {json.dumps(payload, indent=2)}")
            response_data = self._perform_request("POST", url, json=payload)
            logging.info(f"Resposta completa do FileMaker: {json.dumps(response_data, indent=2)}")

        except ValueError:
            logging.error(f"Formato de data inválido recebido: {date_from}, {date_to}")
            return []
        except Exception as e:
            logging.error(f"Um erro inesperado ocorreu durante a busca de leads: {e}")
            return []

        if not response_data:
            logging.error("Nenhuma resposta do FileMaker ao executar _find.")
            return []

        leads = response_data.get("response", {}).get("data", [])
        
        if not leads:
            fm_error_code = response_data.get("messages", [{}])[0].get("code")
            if fm_error_code == "0" or fm_error_code == "401":
                logging.warning("Busca (_find) executada com sucesso, mas nenhum lead encontrado.")
            else:
                logging.error(f"Erro na busca (_find) do FileMaker. Resposta: {response_data}")
            return []

        logging.info(f"Encontrados {len(leads)} leads. Buscando propostas relacionadas...")
        
        results = []
        for lead in leads:
            lead_data = lead.get("fieldData", {})
            
            # =================================================================
            # CORREÇÃO PRINCIPAL AQUI
            # O campo de ID no seu JSON de resposta se chama "id" e não "lead::id"
            # =================================================================
            lead_id = lead_data.get("id")
            
            if not lead_id:
                logging.warning(f"Lead sem ID encontrado, pulando registro: {lead_data}")
                continue

            propostas = self._get_proposals_for_lead(str(lead_id))
            
            if not propostas:
                results.append({
                    "lead_id": str(lead_id),
                    "proposta_id": None,
                    "lead_fields": lead_data,
                    "proposta_fields": {}
                })
            else:
                for proposta in propostas:
                    results.append({
                        "lead_id": str(lead_id),
                        "proposta_id": proposta.get("id"),
                        "lead_fields": lead_data,
                        "proposta_fields": proposta
                    })

        logging.info(f"Processamento finalizado. {len(results)} resultados (leads + propostas) gerados.")
        return results

    def _get_proposals_for_lead(self, lead_id: str) -> List[Dict[str, Any]]:
        """Busca propostas relacionadas a um ID de lead específico."""
        proposal_link_field = os.getenv("FM_PROPOSAL_LINK_FIELD")
        if not proposal_link_field:
            logging.error("O campo de vínculo da proposta (FM_PROPOSAL_LINK_FIELD) não está configurado no .env")
            return []
            
        query = [{proposal_link_field: f"=={lead_id}"}]
        find_payload = {"query": query, "limit": 100}
        url = f"{self.base_url}/layouts/{self.layout_proposta}/_find"
        
        response_data = self._perform_request("POST", url, json=find_payload)
        
        if response_data and response_data.get("response", {}).get("data"):
            return [record["fieldData"] for record in response_data["response"]["data"]]
            
        logging.info(f"Nenhuma proposta encontrada para o lead ID: {lead_id}")
        return []