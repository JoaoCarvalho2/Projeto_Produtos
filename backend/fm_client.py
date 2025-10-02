import os
import requests
import base64
import logging
import json
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
        self.field_fabricante = os.getenv("FM_FIELD_FABRICANTE")
        self.proposal_link_field = os.getenv("FM_PROPOSAL_LINK_FIELD")
        self.ssl_verify = os.getenv("DISABLE_SSL_VERIFY", "false").lower() != "true"
        if not self.ssl_verify:
            import urllib3
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
            logging.warning("Verificação SSL foi desabilitada. Não recomendado para produção.")
        self.base_url = f"https://{self.host}/fmi/data/vLatest/databases/{self.database}"
        self.token = self._get_token()

    def _get_token(self) -> Optional[str]:
        auth_str = f"{self.user}:{self.password}"
        auth_b64 = base64.b64encode(auth_str.encode()).decode()
        headers = {"Authorization": f"Basic {auth_b64}", "Content-Type": "application/json"}
        url = f"{self.base_url}/sessions"
        try:
            response = requests.post(url, headers=headers, json={}, verify=self.ssl_verify, timeout=10)
            response.raise_for_status()
            token = response.json().get("response", {}).get("token")
            if token:
                logging.info("Token de sessão FileMaker gerado com sucesso.")
                return token
            return None
        except requests.exceptions.RequestException as e:
            logging.error(f"Erro ao autenticar no FileMaker: {e}")
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
            logging.error(f"Erro HTTP na requisição ao FileMaker: {e.response.status_code} - {e.response.text}")
        except requests.exceptions.RequestException as e:
            logging.error(f"Erro na requisição ao FileMaker: {e}")
        return None

    def get_leads_with_proposals(self, fabricante: str, date_from: str, date_to: str) -> List[Dict[str, Any]]:
        logging.info(f"Buscando leads para fabricante '{fabricante}' entre {date_from} e {date_to}.")
        
        # =====================================================================
        # TENTATIVA FINAL: Revertendo para o formato de data americano MM/DD/YYYY
        # =====================================================================
        fm_date_from = f"{date_from[5:7]}/{date_from[8:10]}/{date_from[0:4]}"
        fm_date_to = f"{date_to[5:7]}/{date_to[8:10]}/{date_to[0:4]}"

        query = [{"data_criacao": f"{fm_date_from}...{fm_date_to}"}]
        if fabricante:
            query.append({self.field_fabricante: f"=={fabricante}"})

        find_payload = {"query": query, "limit": 15}
        logging.info(f"Payload de busca enviado ao FileMaker: {json.dumps(find_payload, indent=2)}")
        url = f"{self.base_url}/layouts/{self.layout_lead}/_find"
        
        response_data = self._perform_request("POST", url, json=find_payload)
        
        if not response_data or not response_data.get("response", {}).get("data"):
            logging.warning("Nenhum lead encontrado para os filtros fornecidos.")
            return []

        leads = response_data["response"]["data"]
        results = []
        logging.info(f"Encontrados {len(leads)} leads. Buscando propostas para cada um...")
        for lead_record in leads:
            lead_data = lead_record["fieldData"]
            lead_id = lead_data.get("id")
            if not lead_id: continue
            propostas = self._get_proposals_for_lead(lead_id)
            if not propostas:
                results.append({"lead_id": lead_id, "proposta_id": None, "lead_fields": lead_data, "proposta_fields": {}})
            else:
                for proposta_data in propostas:
                    results.append({"lead_id": lead_id, "proposta_id": proposta_data.get("proposta::id"), "lead_fields": lead_data, "proposta_fields": proposta_data})
        logging.info(f"Processamento concluído. Total de {len(results)} linhas de resultado geradas.")
        return results

    def _get_proposals_for_lead(self, lead_id: str) -> List[Dict[str, Any]]:
        if not self.proposal_link_field:
            logging.error("O campo de vínculo da proposta (FM_PROPOSAL_LINK_FIELD) não está configurado no .env")
            return []
        query = [{self.proposal_link_field: f"=={lead_id}"}]
        find_payload = {"query": query, "limit": 100}
        url = f"{self.base_url}/layouts/{self.layout_proposta}/_find"
        response_data = self._perform_request("POST", url, json=find_payload)
        if response_data and response_data.get("response", {}).get("data"):
            return [record["fieldData"] for record in response_data["response"]["data"]]
        logging.warning(f"Nenhuma proposta encontrada para o lead ID: {lead_id}")
        return []