import os
import requests
from requests.auth import HTTPBasicAuth
import base64
import json
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple
from .mappings import status_map, pais_map, vendedor_map, categoria_map, vendedor_email_map, produtos_map

from .mappings import status_map, pais_map, vendedor_map, categoria_map, vendedor_email_map

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

auth = HTTPBasicAuth(os.getenv("JIRA_EMAIL"), os.getenv("JIRA_API_TOKEN"))

class JiraClient:
    def __init__(self):
        self.base_url = os.getenv("JIRA_URL")
        self.email = os.getenv("JIRA_EMAIL")
        self.api_token = os.getenv("JIRA_API_TOKEN")
        # ID do contexto para o campo "Cliente" (customfield_11700)
        self.cliente_context_id = os.getenv("JIRA_CLIENTE_CONTEXT_ID", "12330")
        
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

    def find_issue_by_lead_id(self, lead_id: str, project_key: str) -> Optional[Dict[str, Any]]:
        # ATUALIZADO: customfield_11724 = nº Lead
        jql = f'project = "{project_key}" AND customfield_11724 ~ "{lead_id}"'
        url = f"{self.base_url}/rest/api/3/search/jql" 
        payload = {"jql": jql, "fields": ["id", "key", "customfield_11724"], "maxResults": 1}
        try:
            response = requests.post(url, json=payload, headers=self.headers, timeout=10)
            response.raise_for_status() 
            data = response.json()
            if data.get("issues"):
                return data["issues"][0]
            return None
        except:
            return None

    def delete_issue(self, issue_key: str) -> bool:
        url = f"{self.base_url}/rest/api/3/issue/{issue_key}"
        try:
            requests.delete(url, headers=self.headers, timeout=15)
            return True
        except:
            return False

    def add_comment(self, issue_key: str, content_nodes: List[Dict]) -> bool:
        if not content_nodes: return True
        url = f"{self.base_url}/rest/api/3/issue/{issue_key}/comment"
        payload = {"body": {"type": "doc", "version": 1, "content": content_nodes}}
        try:
            requests.post(url, headers=self.headers, json=payload, timeout=15)
            return True
        except:
            return False

    def _format_comment_from_data(self, proposta_fields: Dict, follows_list: List[Dict], extra_info: str = None) -> List[Dict]:
        content_nodes = []
        
        if extra_info:
            content_nodes.append({
                "type": "panel",
                "attrs": {"panelType": "info"},
                "content": [{
                    "type": "paragraph",
                    "content": [{"type": "text", "text": extra_info}]
                }]
            })

        nome_produto = proposta_fields.get("nome_produto")
        valor_total = proposta_fields.get("valor_total_reais")

        if nome_produto:
            content_nodes.append({"type": "heading", "attrs": {"level": 2}, "content": [{"type": "text", "text": "Produtos / Detalhes"}]})
            content_nodes.append({"type": "paragraph", "content": [{"type": "text", "text": f"{nome_produto} - Valor: {valor_total or '0'}"}]})

        if follows_list:
            content_nodes.append({"type": "heading", "attrs": {"level": 2}, "content": [{"type": "text", "text": "Follow-ups"}]})
            for f in follows_list:
                data = f.get("data_criacao", "")
                usuario = f.get("usuario_criacao", "")
                info = f.get("informacoes", "N/A")
                content_nodes.append({
                    "type": "paragraph",
                    "content": [
                        {"type": "text", "text": f"{data} ({usuario}): ", "marks": [{"type": "em"}]},
                        {"type": "text", "text": info}
                    ]
                })
        return content_nodes

    def _map_fields(self, lead_fields: Dict, proposta_fields: Dict) -> Dict:
        fields_update = {}
        fd = lead_fields
        fp = proposta_fields
        
        
        # 1. ID Lead -> customfield_11724
        lead_id = fd.get("id")
        if lead_id: fields_update["customfield_11724"] = str(lead_id)
        
        # 2. Empresa -> customfield_11733 (Empresa) e customfield_11700 (Cliente - Contexto)
        empresa = fd.get("empresa")
        if empresa: 
            fields_update["summary"] = empresa
            fields_update["customfield_11733"] = empresa
            fields_update["customfield_11700"] = {"value": empresa}
            
        # 3. Nome Contato -> customfield_11739
        if fd.get("nome"): fields_update["customfield_11739"] = fd["nome"]
        
        # 4. Email -> customfield_11760
        if fd.get("email"): fields_update["customfield_11760"] = fd["email"]
        
        # 5. Telefone -> customfield_11213
        if fd.get("telefone"): fields_update["customfield_11213"] = fd["telefone"]
        
        # 6. Status Lead -> customfield_11775
        status = fd.get("status")
        if status and status in status_map: 
            fields_update["customfield_11775"] = {"id": status_map[fd["status"]]}
            
        # 7. Data Criação -> customfield_11687
        if fd.get("data_criacao"): fields_update["customfield_11687"] = self._format_date(fd["data_criacao"])
        
        # 8. País -> customfield_11689 (Pais migrated)
        pais = fd.get("pais")
        if pais and pais in pais_map: 
            fields_update["customfield_11689"] = {"id": pais_map[pais]}
            
        # 9. Vendedor -> customfield_11751 (ID) e customfield_11716 (Email)
        vendedor = fd.get("vendedor.lead::nome_usuario")
        if vendedor:
            if vendedor in vendedor_map: fields_update["customfield_11751"] = {"id": vendedor_map[vendedor]}
            if vendedor in vendedor_email_map: fields_update["customfield_11716"] = vendedor_email_map[vendedor]
            
        # 10. Categoria -> customfield_11766 (Perfil)
        categoria = fp.get("cliente.proposta::categoria") or fd.get("cliente.lead::categoria")
        if categoria and categoria in categoria_map: 
            fields_update["customfield_11766"] = {"id": categoria_map[categoria]}
        
        # --- PROPOSTA ---
        
        # 11. Valor Proposta -> customfield_11710 (Atenção: Usei 11710 pois é "Valor Proposta", 11705 é "Valor Total")
        valor_str = fp.get("valor_total_reais")
        if valor_str:
            try: fields_update["customfield_11710"] = float(valor_str)
            except: pass

        # 12. Validade -> customfield_11715
        if fp.get("proposta::data_validade"): fields_update["customfield_11715"] = self._format_date(fp["proposta::data_validade"])
        
        # 13. Previsão Fechamento -> duedate
        if fp.get("proposta::previsao_fechamento"): fields_update["duedate"] = self._format_date(fp["proposta::previsao_fechamento"])
        
        # 14. Data Follow-up -> customfield_11719
        if fp.get("proposta::data_follow_up"): fields_update["customfield_11719"] = self._format_date(fp["proposta::data_follow_up"])
        
        # 15. Status Proposta -> customfield_11772
        #status_proposta = fp.get("proposta::status")
        #if status_proposta: fields_update["customfield_11772"] = status_proposta

        # 16. N° Proposta -> customfield_11696 (Opção migrated)
        id_proposta = fp.get("id_proposta")
        if id_proposta: fields_update["customfield_11696"] = str(id_proposta)

        # 17. Nome Produto -> customfield_11711
# 17. Nome Produto -> customfield_11711
# jira_client.py

# ... (certifique-se de importar produtos_map no topo do arquivo)


    # DENTRO DA FUNÇÃO _map_fields:

        # 17. Nome Produto -> customfield_11711 (Lógica "Contém")
        nome_produto = fp.get("nome_produto")
        
        if nome_produto:
            found_match = False
            # Percorre cada chave do mapa (ex: "Jira", "Trello")
            for chave, id_jira in produtos_map.items():
                # Verifica se a chave está dentro do nome do produto (ignorando maiúsculas/minúsculas)
                if chave.lower() in nome_produto.lower():
                    fields_update["customfield_11711"] = {"id": id_jira}
                    found_match = True
                    break # Para no primeiro match encontrado
            
            # (Opcional) Se não achou nenhuma palavra-chave, tenta passar o valor exato se soubermos o ID
            # if not found_match:
            #    logging.warning(f"Produto não mapeado: {nome_produto}")
        
        #elif "Trello" in nome_produto: fields_update["customfield_11711"] = "Trello"
        #else nome_produto: fields_update["customfield_11711"] = "Jira Service Managment"
        #if nome_produto: fields_update["customfield_11711"] = nome_produto

        #pais = fd.get("pais")
        #if pais and pais in pais_map: 
        #fields_update["customfield_11689"] = {"id": pais_map[pais]}

        return fields_update
    
    def _ensure_custom_field_option(self, field_key: str, context_id: str, option_value: str) -> bool:
        if not option_value: return True
        base_option_url = f"{self.base_url}/rest/api/3/field/{field_key}/context/{context_id}/option"
        try:
            params = {"query": option_value, "startAt": 0, "maxResults": 25}
            response = requests.get(base_option_url, headers=self.headers, params=params, timeout=5)
            if response.status_code == 200:
                for option in response.json().get("values", []):
                    if option.get("value") == option_value: return True
            payload = {"options": [{"value": option_value}]}
            requests.post(base_option_url, headers=self.headers, json=payload, timeout=10)
            return True
        except: return False

    def create_and_update_issue(self, project_key: str, lead_fields: Dict, proposta_fields: Dict, follows_list: List[Dict]) -> Tuple[str, Optional[str], Optional[str]]:
        summary = lead_fields.get("empresa") or f"Novo Lead"
        lead_id = str(lead_fields.get("id"))
        
        # Criação: Removemos customfield_11724 daqui para evitar erro de "Field not on screen" na criação
        create_payload = {
            "fields": {
                "project": {"key": project_key}, 
                "issuetype": {"name": "Lead"}, 
                "summary": summary
            }
        }
        
        url = f"{self.base_url}/rest/api/3/issue"
        try:
            logging.info(f"CRIANDO Issue Lead {lead_id}...")
            response = requests.post(url, headers=self.headers, json=create_payload, timeout=15)
            
            if response.status_code != 201:
                logging.error(f"Erro Criação Jira: {response.text}")
                return "error", None, f"Erro na criação: {response.text}"
            
            issue_key = response.json()["key"]
            logging.info(f"Issue criada: {issue_key}. Iniciando Update...")
            
            # Tenta preencher os campos personalizados
            action, _, update_message = self.update_issue(issue_key, lead_fields, proposta_fields, is_creation=True)
            
            # PLANO B: Se falhar o update (bloqueio de tela), joga na descrição
            fallback_note = None
            if update_message:
                logging.error(f"FALHA UPDATE: {update_message}")
                logging.info("Aplicando PLANO B: Salvando dados na DESCRIÇÃO...")
                
                desc_text = self._build_description_text(lead_fields, proposta_fields)
                fallback_success = self.update_description(issue_key, desc_text)
                
                if fallback_success:
                    fallback_note = f"⚠️ Nota: Dados salvos na Descrição (Erro de tela no Jira: {update_message})"
                    action = "partial_success"
                    update_message = None # Considera sucesso
                else:
                    return "error", issue_key, f"Falha total. Erro: {update_message}"

            # Comentários
            comment_content = self._format_comment_from_data(proposta_fields, follows_list, extra_info=fallback_note)
            self.add_comment(issue_key, comment_content)

            return action, issue_key, update_message
        except requests.exceptions.RequestException as e:
            return "error", None, str(e)

    def update_issue(self, issue_key: str, lead_fields: Dict, proposta_fields: Dict, is_creation: bool = False) -> Tuple[str, Optional[str], Optional[str]]:
        mapped_fields = self._map_fields(lead_fields, proposta_fields)
        
        # Cliente (11700)
        if "customfield_11700" in mapped_fields and self.cliente_context_id:
             self._ensure_custom_field_option("customfield_11700", self.cliente_context_id, mapped_fields["customfield_11700"]["value"])

        mapped_fields.pop("summary", None)
        payload = {"fields": mapped_fields}
        url = f"{self.base_url}/rest/api/3/issue/{issue_key}"
        
        response = requests.put(url, headers=self.headers, json=payload, timeout=15)
        if response.status_code == 204:
            return ("recreated" if is_creation else "updated"), issue_key, None
        
        return "error", issue_key, f"Erro {response.status_code}: {response.text}"

    def update_description(self, issue_key: str, description_adf: Dict) -> bool:
        payload = {"fields": {"description": description_adf}}
        url = f"{self.base_url}/rest/api/3/issue/{issue_key}"
        try:
            requests.put(url, headers=self.headers, json=payload, timeout=15)
            return True
        except: return False

    def _build_description_text(self, ld: Dict, pf: Dict) -> Dict:
        valor = pf.get("valor_total_reais")
        valor_fmt = f"R$ {valor}" if valor else "N/A"
        text = (
            f"--- DADOS DO LEAD ---\n"
            f"Empresa: {ld.get('empresa', 'N/A')}\n"
            f"Contato: {ld.get('nome', 'N/A')}\n"
            f"Email: {ld.get('email', 'N/A')}\n"
            f"Telefone: {ld.get('telefone', 'N/A')}\n"
            f"ID Lead: {ld.get('id', 'N/A')}\n\n"
            f"--- PROPOSTA ---\n"
            f"Produto: {pf.get('nome_produto', 'N/A')}\n"
            f"Valor: {valor_fmt}\n"
            f"Validade: {pf.get('proposta::data_validade', 'N/A')}"
        )
        return {
            "type": "doc",
            "version": 1,
            "content": [{"type": "paragraph", "content": [{"type": "text", "text": text}]}]
        }