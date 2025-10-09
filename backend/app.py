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

app = FastAPI(
    title="FileMaker to Jira Integrator API",
    description="API para buscar dados no FileMaker e enviá-los para o Jira.",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class SendItem(BaseModel):
    lead_id: str
    proposta_id: str
    lead_fields: Dict
    proposta_fields: Dict

class SendPayload(BaseModel):
    items: List[SendItem]

class SendResult(BaseModel):
    lead_id: str
    proposta_id: str
    action: str
    issue_key: Optional[str] = None
    status: str
    message: Optional[str] = None

fm_client = FileMakerClient()
jira_client = JiraClient()

@app.get("/api/leads", summary="Buscar leads e propostas")
async def search_leads(
    date_from: str = Query(..., description="Data de início no formato YYYY-MM-DD"),
    date_to: str = Query(..., description="Data de fim no formato YYYY-MM-DD")
):
    try:
        # =====================================================================
        # MUDANÇA: O filtro de fabricante foi removido.
        # =====================================================================
        logging.info(f"Iniciando busca por data entre {date_from} e {date_to}.")
        leads_with_proposals = fm_client.get_leads_with_proposals(date_from, date_to)
        return leads_with_proposals
    except Exception as e:
        logging.error(f"Erro ao buscar leads: {e}")
        raise HTTPException(status_code=500, detail="Ocorreu um erro ao buscar dados no FileMaker.")

@app.post("/api/send", response_model=Dict[str, List[SendResult]], summary="Enviar dados para o Jira")
async def send_to_jira(payload: SendPayload):
    results = []
    for item in payload.items:
        lead_id = item.lead_id
        try:
            existing_issue = jira_client.find_issue_by_lead_id(lead_id)
            if existing_issue:
                action, issue_key, message = jira_client.update_issue(
                    existing_issue["key"], item.lead_fields, item.proposta_fields
                )
            else:
                action, issue_key, message = jira_client.create_issue(
                    item.lead_fields, item.proposta_fields
                )
            results.append(SendResult(
                lead_id=lead_id, proposta_id=item.proposta_id, action=action,
                issue_key=issue_key, status="ok" if action in ["created", "updated"] else "error", message=message
            ))
        except Exception as e:
            logging.error(f"Erro inesperado ao processar lead {lead_id}: {e}")
            results.append(SendResult(
                lead_id=lead_id, proposta_id=item.proposta_id, action="error",
                status="error", message=str(e)
            ))
    return {"results": results}