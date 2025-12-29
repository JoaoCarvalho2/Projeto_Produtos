import os
import requests
import base64
import logging
import json
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class FileMakerClient:
    def __init__(self):
        self.host = os.getenv("FM_HOST")
        self.database = os.getenv("FM_DATABASE")
        self.user = os.getenv("FM_USER")
        self.password = os.getenv("FM_PASSWORD")
        
        self.layout_lead = os.getenv("FM_LAYOUT_LEAD", "dados_lead_api")
        self.layout_proposta = os.getenv("FM_LAYOUT_PROPOSTA", "dados_proposta_api")
        self.layout_follow = os.getenv("FM_LAYOUT_FOLLOW", "dados_follow_api")
        
        self.ssl_verify = os.getenv("DISABLE_SSL_VERIFY", "false").lower() != "true"
        if not self.ssl_verify:
            import urllib3
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        
        self.base_url = f"https://{self.host}/fmi/data/vLatest/databases/{self.database}"
        self.token = self._get_token()
        if not self.token:
            # Não quebra o init para permitir que o app suba, mas loga erro
            logging.error("Falha crítica na autenticação com o FileMaker na inicialização.")

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
                return data["response"]["token"]
            return None
        except requests.exceptions.RequestException as e:
            logging.error(f"Erro de conexão CRÍTICO ao autenticar: {e}")
            return None

    def _perform_request(self, method: str, url: str, **kwargs) -> Optional[Dict[str, Any]]:
        if not self.token: 
            self.token = self._get_token()
            if not self.token: return None
            
        headers = {"Authorization": f"Bearer {self.token}", "Content-Type": "application/json"}
        kwargs['headers'] = headers
        kwargs['verify'] = self.ssl_verify
        try:
            if 'json' in kwargs:
                logging.info(f"Enviando FM: {json.dumps(kwargs['json'])}")
            response = requests.request(method, url, **kwargs)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 401:
                logging.warning("Token expirado. Tentando renovar...")
                self.token = self._get_token()
                if self.token: 
                    kwargs['headers']["Authorization"] = f"Bearer {self.token}"
                    return requests.request(method, url, **kwargs).json()
            logging.error(f"Erro HTTP FM ({url}): {e.response.status_code} - {e.response.text}")
        except Exception as e:
            logging.error(f"Erro genérico FM: {e}")
        return None

    def get_leads_with_proposals(self, date_from: str, date_to: str, fornecedor: str) -> List[Dict[str, Any]]:
        try:
            date_from_obj = datetime.strptime(date_from, "%Y-%m-%d")
            date_to_obj = datetime.strptime(date_to, "%Y-%m-%d")
            date_from_fm = date_from_obj.strftime("%m/%d/%Y")
            date_to_fm = date_to_obj.strftime("%m/%d/%Y")
            dates_for_fm = f"{date_from_fm}...{date_to_fm}"
            
            query_payload = {
                "query": [{"data_criacao": dates_for_fm, "fabricante": fornecedor}], 
                "limit": 1000
            }
            url = f"{self.base_url}/layouts/{self.layout_lead}/_find"
            response_data = self._perform_request("POST", url, json=query_payload)
        except Exception as e:
            logging.error(f"Erro busca leads: {e}")
            return []

        if not response_data: return []

        leads = response_data.get("response", {}).get("data", [])
        if not leads: return []

        results = []
        for lead in leads:
            lead_data = lead.get("fieldData", {})
            lead_id = lead_data.get("id")
            if not lead_id: 
                lead_id = lead_data.get("lead::id")
                if not lead_id: continue

            proposta_data, proposta_portals = self._get_latest_proposal_for_lead(str(lead_id))
            
            # Tenta pegar ID da proposta
            proposta_id = proposta_data.get("id_proposta") or proposta_data.get("produto_proposta::id_proposta")
            
            follows_list = []
            if proposta_id:
                follows_list = self._get_follows_for_proposal(str(proposta_id))

            results.append({
                "lead_id": str(lead_id),
                "proposta_id": str(proposta_id) if proposta_id else None,
                "lead_fields": lead_data,
                "proposta_fields": proposta_data,
                "proposta_portals": proposta_portals,
                "follows_list": follows_list
            })

        return results

    def _get_latest_proposal_for_lead(self, lead_id: str) -> Tuple[Dict, Dict]:
        proposal_link_field = os.getenv("FM_PROPOSAL_LINK_FIELD", "lead.proposta::id")
        
        # Busca com ordenação
        query = [{proposal_link_field: f"=={lead_id}"}]
        find_payload = {
            "query": query, 
            "limit": 1,
            "sort": [{"fieldName": "proposta::data_criacao", "sortOrder": "descend"}]
        }
        url = f"{self.base_url}/layouts/{self.layout_proposta}/_find"
        
        response_data = self._perform_request("POST", url, json=find_payload)
        
        if not response_data:
            # Fallback sem ordenação se falhar
            find_payload.pop("sort")
            response_data = self._perform_request("POST", url, json=find_payload)
            if not response_data: return {}, {}
            
        response_obj = response_data.get("response")
        if not response_obj: return {}, {}

        propostas = response_obj.get("data", [])
        if propostas:
            record = propostas[0]
            return record.get("fieldData", {}), record.get("portalData", {})
            
        return {}, {}

    def _get_follows_for_proposal(self, proposta_id: str) -> List[Dict]:
        follow_link_field = os.getenv("FM_FOLLOW_LINK_FIELD", "id_proposta")
        
        query = [{follow_link_field: f"=={proposta_id}"}]
        find_payload = {
            "query": query,
            "limit": 50,
            "sort": [{"fieldName": "data_criacao", "sortOrder": "descend"}]
        }
        
        url = f"{self.base_url}/layouts/{self.layout_follow}/_find"
        response_data = self._perform_request("POST", url, json=find_payload)
        
        if not response_data: return []
        follows_data = response_data.get("response", {}).get("data", [])
        return [f.get("fieldData", {}) for f in follows_data]