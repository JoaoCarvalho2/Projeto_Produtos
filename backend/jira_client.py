import os
import requests
from requests.auth import HTTPBasicAuth
import base64
import json
import logging
import re
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple

from mappings import status_map, pais_map, vendedor_map, categoria_map, vendedor_email_map

auth = HTTPBasicAuth(os.getenv("JIRA_EMAIL"), os.getenv("JIRA_API_TOKEN"))

class JiraClient:
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
        if not date_str: return None
        formats = ["%m/%d/%Y", "%m/%d/%Y %H:%M:%S", "%d/%m/%Y", "%d/%m/%Y %H:%M:%S", "%Y-%m-%d", "%Y-%m-%d %H:%M:%S"]
        for fmt in formats:
            try:
                return datetime.strptime(date_str, fmt).strftime("%Y-%m-%d")
            except ValueError:
                continue
        return None

    def find_issue_by_lead_id(self, lead_id: str) -> Optional[Dict[str, Any]]:

        jql = f'project = "{self.project_key}" AND customfield_10132 ~ "{lead_id}"'
        
        # Este é o endpoint correto para buscas JQL via POST
        url = f"{self.base_url}/rest/api/3/search/jql" 

        # Este é o payload que você testou e funcionou
        payload = json.dumps( {
            "jql": jql,
            "fields": [
                "id",
                "key",
                "cf[10132]",
                "customfield_10132",
                "nº Lead[Short text]"
            ],
            "fieldsByKeys": 'true', # Mantido como string, como no seu exemplo
            "maxResults": 500, # Só precisamos encontrar uma, 5 é mais que suficiente
        } )
        
        logging.info(f"Buscando issue com Lead ID: {lead_id} (JQL: {jql})")
        
        try:
            # A requisição POST correta
            response = requests.request(
                "POST",
                url,
                data=payload,           # Use 'data' para o corpo do POST
                headers=self.headers,   # Use os headers da classe (já contêm auth)
                # Não precisa de 'auth=auth' (já está em self.headers)
                # Não use 'params=payload' (incorreto)
                timeout=10
            )

            # Lança um erro para respostas 4xx ou 5xx
            response.raise_for_status() 
            
            data = response.json()
            
            # O 'print' de debug que você tinha. Pode ser removido se não for necessário.
            print(json.dumps(data, sort_keys=True, indent=4, separators=(",", ": ")))

            # A API /search/jql (POST) retorna o campo "total"
            if data.get("issues") and len(data["issues"]) >= 1:
                # Pega a primeira issue da lista
                issue_data = data["issues"][0] 
                logging.info(f"Issue encontrada para Lead ID {lead_id}: {issue_data['key']}")
                return issue_data
            
            # Se a lista "issues" não existir ou estiver vazia, executa isso:
            logging.info(f"Nenhuma issue encontrada para Lead ID {lead_id}.")
            return None
            
        except requests.exceptions.RequestException as e:
            # O erro será capturado aqui
            logging.error(f"Erro ao buscar issue para Lead ID {lead_id}: {e}")
            if hasattr(e, 'response') and e.response is not None:
                logging.error(f"Detalhe do erro (Response): {e.response.status_code} - {e.response.text}")
            return None

    def delete_issue(self, issue_key: str) -> bool:
            url = f"{self.base_url}/rest/api/3/issue/{issue_key}"
            
            # [NOVO] Log da tentativa de deleção
            logging.info(f"Tentando apagar issue: {issue_key} (URL: {url})")
            
            try:
                response = requests.delete(url, headers=self.headers, timeout=15)
                
                if response.status_code == 204:
                    # Este log já existia e está ótimo! (Adicionei o 'Resultado' para clareza)
                    logging.info(f"Issue {issue_key} apagada com sucesso. (Resultado: True)")
                    return True
                    
                # Este log já existia e está ótimo! (Adicionei o 'Resultado' para clareza)
                logging.error(f"Falha ao apagar issue {issue_key}: {response.status_code}, {response.text} (Resultado: False)")
                return False
                
            except requests.exceptions.RequestException as e:
                # Este log já existia e está ótimo! (Adicionei o 'Resultado' para clareza)
                logging.error(f"Exceção ao apagar issue {issue_key}: {e} (Resultado: False)")
                return False

    def add_comment(self, issue_key: str, content_nodes: List[Dict]) -> bool:
        """ATUALIZADO: Adiciona um comentário a uma issue usando o formato ADF."""
        if not content_nodes: return True
        url = f"{self.base_url}/rest/api/3/issue/{issue_key}/comment"
        # Payload agora usa a estrutura de documento do Atlassian (ADF)
        payload = {"body": {"type": "doc", "version": 1, "content": content_nodes}}
        try:
            response = requests.post(url, headers=self.headers, json=payload, timeout=15)
            if response.status_code == 201:
                logging.info(f"Comentário adicionado com sucesso na issue {issue_key}.")
                return True
            logging.error(f"Falha ao adicionar comentário na issue {issue_key}: {response.status_code}, {response.text}")
            return False
        except requests.exceptions.RequestException as e:
            logging.error(f"Exceção ao adicionar comentário na issue {issue_key}: {e}")
            return False

    def _format_comment_from_portals(self, portals: Dict) -> List[Dict]:
        """REESCRITO: Formata os dados dos portais em uma estrutura de documento ADF para o Jira."""
        content_nodes = []
        
        # Formata produtos
        produtos = portals.get("produto_proposta", [])
        if produtos:
            content_nodes.append({"type": "heading", "attrs": {"level": 2}, "content": [{"type": "text", "text": "Produtos da Proposta"}]})
            
            product_list_items = []
            total_proposta = 0.0
            for p in produtos:
                nome = p.get("produto_proposta::nome_produto", "N/A")
                valor_str = p.get("produto_proposta::valor_total", "0") or "0"
                try: 
                    valor = float(valor_str)
                    total_proposta += valor
                except (ValueError, TypeError): 
                    valor = valor_str # Mantem como texto se não for número
                
                product_list_items.append({
                    "type": "listItem",
                    "content": [{"type": "paragraph", "content": [{"type": "text", "text": f"{nome} - Valor: {valor}"}]}]
                })
            content_nodes.append({"type": "bulletList", "content": product_list_items})
            content_nodes.append({"type": "paragraph", "content": [{"type": "text", "text": f"Valor Total da Proposta: {total_proposta:.2f}", "marks": [{"type": "strong"}]}]})

        # Formata follows
        follows = portals.get("follow.proposta", [])
        if follows:
            content_nodes.append({"type": "heading", "attrs": {"level": 2}, "content": [{"type": "text", "text": "Follow-ups"}]})
            for f in follows:
                data = f.get("follow.proposta::data_hora_criacao", "")
                usuario = f.get("follow.proposta::usuario_criacao", "")
                info = f.get("follow.proposta::informacoes", "N/A")
                
                content_nodes.append({
                    "type": "paragraph",
                    "content": [
                        {"type": "text", "text": f"{data} ({usuario}): ", "marks": [{"type": "em"}]},
                        {"type": "text", "text": info}
                    ]
                })

        return content_nodes

    def _map_fields(self, lead_fields: Dict, proposta_fields: Dict) -> Dict:
        # ... (sem alterações)
        fields_update = {}
        fd=lead_fields; fp=proposta_fields
        if fd.get("id"): fields_update["customfield_10132"] = str(fd["id"])
        empresa = fd.get("empresa")
        if empresa: fields_update["summary"] = empresa; fields_update["customfield_10134"] = empresa; fields_update["customfield_10047"] = {"value": empresa}
        if fd.get("nome"): fields_update["customfield_10151"] = fd["nome"]
        if fd.get("email"): fields_update["customfield_10136"] = fd["email"]
        if fd.get("telefone"): fields_update["customfield_10138"] = fd["telefone"]
        if fd.get("status") in status_map: fields_update["customfield_10141"] = {"id": status_map[fd["status"]]}
        if fd.get("data_criacao"): fields_update["customfield_10140"] = self._format_date(fd["data_criacao"])
        if fd.get("pais") in pais_map: fields_update["customfield_10142"] = {"id": pais_map[fd["pais"]]}
        vendedor = fd.get("vendedor.lead::nome_usuario")
        if vendedor:
            if vendedor in vendedor_map: fields_update["customfield_10146"] = {"id": vendedor_map[vendedor]}
            if vendedor in vendedor_email_map: fields_update["customfield_10500"] = vendedor_email_map[vendedor]
        categoria = fp.get("cliente.proposta::categoria") or fd.get("cliente.lead::categoria")
        if categoria in categoria_map: fields_update["customfield_10135"] = {"id": categoria_map[categoria]}
        if fp.get("produto_proposta::valor_total_sum"):
            try: fields_update["customfield_10148"] = float(fp["produto_proposta::valor_total_sum"])
            except (ValueError, TypeError): pass
        if fp.get("data_validade"): fields_update["customfield_10534"] = self._format_date(fp["data_validade"])
        if fp.get("previsao_fechamento"): fields_update["duedate"] = self._format_date(fp["previsao_fechamento"])
        if fp.get("data_follow_up"): fields_update["customfield_10537"] = self._format_date(fp["data_follow_up"])
        if fd.get("lead::modo_licenciamento"): fields_update["customfield_10147"] = fd["lead::modo_licenciamento"]
        if fp.get("lead.proposta::produto"): fields_update["customfield_10804"] = { "value": str(fp["lead.proposta::produto"]) }
        log_data = fp.get("produto_proposta::LogData")
        if log_data:
            match = re.search(r"\[id_cotacao\].*?-\»\s*(\d+)", log_data)
            if match:
                try: fields_update["customfield_10150"] = int(match.group(1))
                except (ValueError, TypeError): pass
        return fields_update

    def create_and_update_issue(self, lead_fields: Dict, proposta_fields: Dict, proposta_portals: Dict) -> Tuple[str, Optional[str], Optional[str]]:
        """ATUALIZADO: Controla o fluxo de criação, atualização e adição de comentário."""
        summary = lead_fields.get("empresa", f"Novo Lead - {lead_fields.get('id')}")
        lead_id = str(lead_fields.get("id"))
        create_payload = {"fields": {"project": {"key": self.project_key}, "issuetype": {"name": "Lead"}, "summary": summary, "customfield_10132": lead_id}}
        
        url = f"{self.base_url}/rest/api/3/issue"
        try:
            response = requests.post(url, headers=self.headers, json=create_payload, timeout=15)
            if response.status_code != 201:
                return "error", None, f"Erro na criação: {response.text}"
            
            issue_key = response.json()["key"]
            logging.info(f"Issue {issue_key} criada. Atualizando campos...")
            
            action, _, update_message = self.update_issue(issue_key, lead_fields, proposta_fields, is_creation=True)
            if update_message:
                return "error", issue_key, f"Issue criada mas falhou ao atualizar: {update_message}"

            logging.info(f"Issue {issue_key} atualizada. Adicionando comentários...")
            comment_content = self._format_comment_from_portals(proposta_portals)
            comment_ok = self.add_comment(issue_key, comment_content)
            if not comment_ok:
                return "error", issue_key, "Issue criada e atualizada, mas falhou ao adicionar comentário."

            return action, issue_key, None
        except requests.exceptions.RequestException as e:
            return "error", None, str(e)

    def update_issue(self, issue_key: str, lead_fields: Dict, proposta_fields: Dict, is_creation: bool = False) -> Tuple[str, Optional[str], Optional[str]]:
        # ... (sem alterações)
        mapped_fields = self._map_fields(lead_fields, proposta_fields)
        mapped_fields.pop("summary", None)
        mapped_fields.pop("customfield_10132", None)
        payload = {"fields": mapped_fields}
        url = f"{self.base_url}/rest/api/3/issue/{issue_key}"
        try:
            response = requests.put(url, headers=self.headers, json=payload, timeout=15)
            if response.status_code == 204:
                action = "recreated" if is_creation else "updated"
                return action, issue_key, None
            return "error", issue_key, f"Erro {response.status_code}: {response.text}"
        except requests.exceptions.RequestException as e:
            return "error", issue_key, str(e)