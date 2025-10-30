import os
import logging
from typing import List, Dict, Optional

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

from fm_client import FileMakerClient
from jira_client import JiraClient

load_dotenv()
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

app = FastAPI(title="FileMaker to Jira Integrator API")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

class SendItem(BaseModel):
    lead_id: str
    proposta_id: Optional[str] = None
    lead_fields: Dict
    proposta_fields: Dict
    # NOVO: Adiciona os dados do portal ao modelo
    proposta_portals: Dict

class SendPayload(BaseModel):
    items: List[SendItem]
class SendResult(BaseModel):
    lead_id: str
    proposta_id: Optional[str] = None
    action: str
    issue_key: Optional[str] = None
    status: str
    message: Optional[str] = None

fm_client = FileMakerClient()
jira_client = JiraClient()


@app.get("/api/config", summary="Obter configurações do servidor")
async def get_config():
    return {"jira_base_url": os.getenv("JIRA_URL")}

@app.get("/api/leads", summary="Buscar leads e propostas")
async def search_leads(
    date_from: str = Query(..., description="Data de início no formato YYYY-MM-DD"),
    date_to: str = Query(..., description="Data de fim no formato YYYY-MM-DD"),
    fornecedor: str = Query(..., description="Nome do fabricante/fornecedor")
):
    try:
        return fm_client.get_leads_with_proposals(date_from, date_to, fornecedor)
    except Exception as e:
        raise HTTPException(status_code=500, detail="Ocorreu um erro ao buscar dados no FileMaker.")

@app.post("/api/send", response_model=Dict[str, List[SendResult]], summary="Enviar dados para o Jira")
async def send_to_jira(payload: SendPayload):
    """LÓGICA ATUALIZADA: Deletar issue existente antes de criar uma nova e adicionar comentários."""
    results = []
    for item in payload.items:
        lead_id = item.lead_id
        try:
            # 1. Procura se a issue já existe
            existing_issue = jira_client.find_issue_by_lead_id(lead_id)
            if existing_issue:
                # 2. Se existir, apaga a issue antiga
                logging.info(f"Issue {existing_issue['key']} encontrada. Deletando para recriar...")
                jira_client.delete_issue(existing_issue['key'])
            
            # 3. Cria uma nova issue, atualiza e adiciona comentários
            action, issue_key, message = jira_client.create_and_update_issue(
                item.lead_fields, item.proposta_fields, item.proposta_portals
            )
            
            results.append(SendResult(
                lead_id=lead_id, proposta_id=item.proposta_id, action=action,
                issue_key=issue_key, status="ok" if message is None else "error", message=message
            ))
        except Exception as e:
            logging.error(f"Erro inesperado ao processar lead {lead_id}: {e}")
            results.append(SendResult(
                lead_id=lead_id, proposta_id=item.proposta_id, action="fatal_error",
                status="error", message=str(e)
            ))
    return {"results": results}