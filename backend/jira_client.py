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
        formats = ["%m/%d/%Y", "%m/%d/%Y %H:%M:%S", "%d/%m/%Y", "%d/%m/%Y %H:%M:%S", "%Y-%m-%d", "%Y-%m-%d %H:%M:%S"]
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
                logging.info(f"Issue existente encontrada para o lead ID {lead_id}: {issue['key']}")
                return issue
            return None
        except requests.exceptions.RequestException as e:
            logging.error(f"Erro ao buscar issue no Jira para o lead ID {lead_id}: {e}")
            return None

    def _map_fields(self, lead_fields: Dict[str, Any], proposta_fields: Dict[str, Any]) -> Dict[str, Any]:
        """Mapeia os campos do FileMaker para o formato esperado pelo Jira, incluindo lógicas do script de teste."""
        fields_update = {}
        fd = lead_fields
        fp = proposta_fields

        # --- Campos do Lead (fd) ---
        if fd.get("id"):
            fields_update["customfield_10132"] = str(fd["id"])
        
        empresa = fd.get("empresa")
        if empresa:
            fields_update["summary"] = empresa
            fields_update["customfield_10134"] = empresa
            fields_update["customfield_10047"] = {"value": empresa}
        
        if fd.get("nome"):
            fields_update["customfield_10151"] = fd["nome"]
        if fd.get("email"):
            fields_update["customfield_10136"] = fd["email"]
        if fd.get("telefone"):
            fields_update["customfield_10138"] = fd["telefone"]
        if fd.get("status") in status_map:
            fields_update["customfield_10141"] = {"id": status_map[fd["status"]]}
        if fd.get("data_criacao"):
            fields_update["customfield_10140"] = self._format_date(fd["data_criacao"])
        if fd.get("pais") in pais_map:
            fields_update["customfield_10142"] = {"id": pais_map[fd["pais"]]}
            
        vendedor = fd.get("vendedor.lead::nome_usuario")
        if vendedor:
            if vendedor in vendedor_map:
                fields_update["customfield_10146"] = {"id": vendedor_map[vendedor]}
            if vendedor in vendedor_email_map:
                fields_update["customfield_10500"] = vendedor_email_map[vendedor]

        # --- Campos da Proposta (fp) ou Fallback para o Lead ---
        categoria = fp.get("cliente.proposta::categoria") or fd.get("cliente.lead::categoria")
        if categoria in categoria_map:
            fields_update["customfield_10135"] = {"id": categoria_map[categoria]}

        if fp.get("produto_proposta::valor_total_sum"):
            try:
                fields_update["customfield_10148"] = float(fp["produto_proposta::valor_total_sum"])
            except (ValueError, TypeError):
                logging.warning(f"Valor da proposta inválido: {fp.get('produto_proposta::valor_total_sum')}")
        
        if fp.get("data_validade"):
            fields_update["customfield_10534"] = self._format_date(fp["data_validade"])
        if fp.get("previsao_fechamento"):
            fields_update["duedate"] = self._format_date(fp["previsao_fechamento"])
            
        # =================================================================
        # LÓGICA ADICIONADA DO SCRIPT testecomjira.py
        # =================================================================
        if fp.get("data_follow_up"):
            fields_update["customfield_10537"] = self._format_date(fp["data_follow_up"])
            
        if fd.get("lead::modo_licenciamento"):
            fields_update["customfield_10147"] = fd["lead::modo_licenciamento"]

        if fp.get("lead.proposta::produto"): 
            fields_update["customfield_10804"] = { "value": str(fp["lead.proposta::produto"]) }

        # Extraindo ID da Cotação do LogData
        log_data = fp.get("produto_proposta::LogData")
        if log_data:
            match = re.search(r"\[id_cotacao\].*?-\»\s*(\d+)", log_data)
            if match:
                try:
                    id_cotacao = int(match.group(1))
                    fields_update["customfield_10150"] = id_cotacao
                    logging.info(f"ID da cotação {id_cotacao} extraído do log para o lead {fd.get('id')}")
                except (ValueError, TypeError):
                     logging.warning(f"ID da cotação encontrado no log não é um número válido: {match.group(1)}")
        # =================================================================
        
        return fields_update

    def create_and_update_issue(self, lead_fields: Dict, proposta_fields: Dict) -> Tuple[str, Optional[str], Optional[str]]:
        """Cria uma issue com o mínimo de campos e depois a atualiza com o restante dos dados."""
        summary = lead_fields.get("empresa", f"Novo Lead - {lead_fields.get('id')}")
        lead_id = str(lead_fields.get("id"))
        
        create_payload = {
            "fields": {
                "project": {"key": self.project_key},
                "issuetype": {"name": "Lead"},
                "summary": summary,
                "customfield_10132": lead_id
            }
        }
        
        url = f"{self.base_url}/rest/api/3/issue"
        try:
            response = requests.post(url, headers=self.headers, json=create_payload, timeout=15)
            if response.status_code != 201:
                error_msg = f"Erro {response.status_code} na criação inicial: {response.text}"
                logging.error(f"Falha ao criar issue: {error_msg}")
                return "error", None, error_msg
            
            issue_key = response.json()["key"]
            logging.info(f"Issue {issue_key} criada (passo 1/2). Atualizando com os demais campos...")
            return self.update_issue(issue_key, lead_fields, proposta_fields, is_creation=True)
        except requests.exceptions.RequestException as e:
            logging.error(f"Exceção ao criar issue: {e}")
            return "error", None, str(e)

    def update_issue(self, issue_key: str, lead_fields: Dict, proposta_fields: Dict, is_creation: bool = False) -> Tuple[str, Optional[str], Optional[str]]:
        """Atualiza uma issue existente no Jira."""
        mapped_fields = self._map_fields(lead_fields, proposta_fields)
        mapped_fields.pop("summary", None)
        mapped_fields.pop("customfield_10132", None)

        payload = {"fields": mapped_fields}
        url = f"{self.base_url}/rest/api/3/issue/{issue_key}"

        try:
            response = requests.put(url, headers=self.headers, json=payload, timeout=15)
            if response.status_code == 204:
                action = "created" if is_creation else "updated"
                logging.info(f"Issue {issue_key} {'preenchida' if is_creation else 'atualizada'} com sucesso.")
                return action, issue_key, None
            else:
                error_msg = f"Erro {response.status_code}: {response.text}"
                logging.error(f"Falha ao atualizar issue {issue_key}: {error_msg}")
                return "error", issue_key, error_msg
        except requests.exceptions.RequestException as e:
            logging.error(f"Exceção ao atualizar issue {issue_key}: {e}")
            return "error", issue_key, str(e)