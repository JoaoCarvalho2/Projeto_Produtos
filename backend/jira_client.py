import os
import requests
import base64
import logging
import re
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple

from mappings import status_map, pais_map, vendedor_map, categoria_map, vendedor_email_map

class JiraClient:
    """Cliente para interagir com a API do Jira."""

    def __init__(self):
        self.base_url = os.getenv("JIRA_URL")
        self.email = os.getenv("JIRA_EMAIL")
        self.api_token = os.getenv("JIRA_API_TOKEN")
        self.project_key = os.getenv("JIRA_PROJECT_KEY")
        
        auth_str = f"{self.email}:{self.api_token}"
        auth_b64 = base64.b64encode(auth_str.encode()).decode()
        self.headers = {
            "Authorization": f"Basic {auth_b64}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        
    def _format_date(self, date_str: str) -> Optional[str]:
        """Normaliza diferentes formatos de data para YYYY-MM-DD."""
        if not date_str:
            return None
        formats = ["%Y-%m-%d %H:%M:%S", "%Y-%m-%d", "%d/%m/%Y", "%d/%m/%Y %H:%M:%S", "%m/%d/%Y", "%m/%d/%Y %H:%M:%S"]
        for fmt in formats:
            try:
                return datetime.strptime(date_str, fmt).strftime("%Y-%m-%d")
            except ValueError:
                continue
        logging.warning(f"Data em formato inesperado não pôde ser convertida: {date_str}")
        return None

    def find_issue_by_lead_id(self, lead_id: str) -> Optional[Dict[str, Any]]:
        """Busca uma issue no Jira pelo campo customizado que armazena o ID do lead."""
        jql = f'project = "{self.project_key}" AND cf[10132] ~ "{lead_id}"'
        url = f"{self.base_url}/rest/api/3/search"
        payload = {"jql": jql, "fields": ["id", "key"]}

        try:
            response = requests.post(url, headers=self.headers, json=payload, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if data.get("total", 0) >= 1:
                issue = data["issues"][0]
                if data.get("total", 0) > 1:
                    logging.warning(f"Múltiplas issues encontradas para o lead ID {lead_id}. A primeira ({issue['key']}) será usada.")
                else:
                    logging.info(f"Issue existente encontrada para o lead ID {lead_id}: {issue['key']}")
                return issue
            else:
                logging.info(f"Nenhuma issue encontrada para o lead ID {lead_id}.")
                return None
        except requests.exceptions.RequestException as e:
            logging.error(f"Erro ao buscar issue no Jira para o lead ID {lead_id}: {e}")
            return None

    def _map_fields(self, lead_fields: Dict[str, Any], proposta_fields: Dict[str, Any]) -> Dict[str, Any]:
        """Mapeia os campos do FileMaker para o formato esperado pelo Jira."""
        fields_update = {}
        fd = lead_fields
        fp = proposta_fields

        if fd.get("id"):
            fields_update["customfield_10132"] = str(fd["id"])

        if fd.get("status") in status_map:
            fields_update["customfield_10141"] = {"id": status_map[fd["status"]]}

        if fp.get("cliente.proposta::categoria") in categoria_map:
            fields_update["customfield_10135"] = {"id": categoria_map[fp["cliente.proposta::categoria"]]}

        if fd.get("lead::modo_licenciamento"):
            fields_update["customfield_10147"] = fd["lead::modo_licenciamento"]
            
        if fd.get("data_criacao"):
            fields_update["customfield_10140"] = self._format_date(fd["data_criacao"])

        if fp.get("lead.proposta::produto"):  
            fields_update["customfield_10804"] = {"value": str(fp["lead.proposta::produto"])}

        vendedor = fd.get("vendedor.lead::nome_usuario")
        if vendedor:
            if vendedor in vendedor_map:
                fields_update["customfield_10146"] = {"id": vendedor_map[vendedor]}
            if vendedor in vendedor_email_map:
                fields_update["customfield_10500"] = vendedor_email_map[vendedor]
        
        empresa = fd.get("empresa")
        if empresa:
            fields_update["summary"] = empresa
            fields_update["customfield_10134"] = empresa
            fields_update["customfield_10047"] = {"value": empresa}

        if fd.get("telefone"):
            fields_update["customfield_10138"] = fd["telefone"]

        if fp.get("pais") in pais_map:
            fields_update["customfield_10142"] = {"id": pais_map[fp["pais"]]}
            
        if fd.get("nome"):
            fields_update["customfield_10151"] = fd["nome"]
            
        if fd.get("email"):
            fields_update["customfield_10136"] = fd["email"]

        if fp.get("produto_proposta::valor_total_sum"):
            try:
                fields_update["customfield_10148"] = float(fp["produto_proposta::valor_total_sum"])
            except (ValueError, TypeError):
                logging.warning(f"Não foi possível converter 'valor_total_sum' para float: {fp.get('produto_proposta::valor_total_sum')}")
        
        if fp.get("data_validade"):
            fields_update["customfield_10534"] = self._format_date(fp["data_validade"])
            
        if fp.get("data_follow_up"):
            fields_update["customfield_10537"] = self._format_date(fp["data_follow_up"])
            
        if fp.get("previsao_fechamento"):
            fields_update["duedate"] = self._format_date(fp["previsao_fechamento"])
            
        log_data = fp.get("produto_proposta::LogData", "")
        if log_data:
            match = re.search(r"\[id_cotacao\].*?-\»\s*(\d+)", log_data)
            if match:
                id_cotacao = int(match.group(1))
                fields_update["customfield_10150"] = id_cotacao
                logging.info(f"ID da cotação encontrado: {id_cotacao}")

        return fields_update

    def create_issue(self, lead_fields: Dict, proposta_fields: Dict) -> Tuple[str, Optional[str], Optional[str]]:
        """Cria uma nova issue no Jira."""
        mapped_fields = self._map_fields(lead_fields, proposta_fields)
        
        payload = {
            "fields": {
                "project": {"key": self.project_key},
                "issuetype": {"name": "Lead"},
                "summary": mapped_fields.get("summary", f"Novo Lead - {lead_fields.get('id')}"),
                **mapped_fields
            }
        }
        
        url = f"{self.base_url}/rest/api/3/issue"
        try:
            response = requests.post(url, headers=self.headers, json=payload, timeout=15)
            if response.status_code == 201:
                issue_key = response.json()["key"]
                logging.info(f"Issue {issue_key} criada com sucesso para o lead ID {lead_fields.get('id')}.")
                return "created", issue_key, None
            else:
                error_msg = f"Erro {response.status_code}: {response.text}"
                logging.error(f"Falha ao criar issue: {error_msg}")
                return "error", None, error_msg
        except requests.exceptions.RequestException as e:
            logging.error(f"Exceção ao criar issue: {e}")
            return "error", None, str(e)

    def update_issue(self, issue_key: str, lead_fields: Dict, proposta_fields: Dict) -> Tuple[str, Optional[str], Optional[str]]:
        """Atualiza uma issue existente no Jira."""
        mapped_fields = self._map_fields(lead_fields, proposta_fields)
        
        payload = {"fields": mapped_fields}
        url = f"{self.base_url}/rest/api/3/issue/{issue_key}"

        try:
            response = requests.put(url, headers=self.headers, json=payload, timeout=15)
            if response.status_code == 204:
                logging.info(f"Issue {issue_key} atualizada com sucesso.")
                return "updated", issue_key, None
            else:
                error_msg = f"Erro {response.status_code}: {response.text}"
                logging.error(f"Falha ao atualizar issue {issue_key}: {error_msg}")
                return "error", issue_key, error_msg
        except requests.exceptions.RequestException as e:
            logging.error(f"Exceção ao atualizar issue {issue_key}: {e}")
            return "error", issue_key, str(e)