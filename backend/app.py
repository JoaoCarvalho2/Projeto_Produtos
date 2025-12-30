import os
import logging
from typing import List, Dict, Optional, Any
from fastapi import BackgroundTasks
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
from fastapi.staticfiles import StaticFiles
from starlette.responses import FileResponse

from .fm_client import FileMakerClient
from .jira_client import JiraClient

APP_DIR = os.path.dirname(os.path.abspath(__file__))
DOTENV_PATH = os.path.normpath(os.path.join(APP_DIR, "..", ".env"))
load_dotenv(dotenv_path=DOTENV_PATH)

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

app = FastAPI(title="FileMaker to Jira Integrator API")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

# --- CLASSES Pydantic Atualizadas ---
class SendItem(BaseModel):
    lead_id: str
    proposta_id: Optional[str] = None
    lead_fields: Dict[str, Any]
    proposta_fields: Dict[str, Any]
    proposta_portals: Dict[str, Any] = {} # Mantido para compatibilidade, mas pode vir vazio
    follows_list: List[Dict[str, Any]] = [] # Novo campo para a lista de follows

class SendPayload(BaseModel):
    items: List[SendItem]
    fornecedor: str

class SendResult(BaseModel):
    lead_id: str
    proposta_id: Optional[str] = None
    action: str
    issue_key: Optional[str] = None
    status: str
    message: Optional[str] = None
# --- FIM DAS CLASSES ---

fm_client = FileMakerClient()
jira_client = JiraClient()

@app.get("/api/config")
async def get_config():
    return {"jira_base_url": os.getenv("JIRA_URL")}

@app.get("/api/leads")
async def search_leads(
    date_from: str = Query(...),
    date_to: str = Query(...),
    fornecedor: str = Query(...)
):
    try:
        return fm_client.get_leads_with_proposals(date_from, date_to, fornecedor)
    except Exception as e:
        logging.error(f"Erro detalhado ao buscar leads: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Ocorreu um erro ao buscar dados no FileMaker.")

@app.post("/api/send", response_model=Dict[str, List[SendResult]])
async def send_to_jira(payload: SendPayload):
    PROJECT_KEYS_MAP = {
        "Atlassian": os.getenv("JIRA_PROJECT_KEY_ATLASSIAN"),
        "Anydesk": os.getenv("JIRA_PROJECT_KEY_ANYDESK"),
        "SonarQube": os.getenv("JIRA_PROJECT_KEY_SONARQUBE")
    }

    fornecedor = payload.fornecedor
    project_key = PROJECT_KEYS_MAP.get(fornecedor)

    if not project_key:
        results = [SendResult(
                lead_id=item.lead_id, proposta_id=item.proposta_id, action="config_error",
                status="error", message=f"Chave de projeto não configurada para '{fornecedor}'"
            ) for item in payload.items]
        return {"results": results}
    
    results = []
    for item in payload.items:
        lead_id = item.lead_id
        try:
            existing_issue = jira_client.find_issue_by_lead_id(lead_id, project_key) 
            if existing_issue:
                jira_client.delete_issue(existing_issue['key'])
            
            # Passando follows_list separadamente
            action, issue_key, message = jira_client.create_and_update_issue(
                project_key,  
                item.lead_fields, 
                item.proposta_fields, 
                item.follows_list
            )
            
            results.append(SendResult(
                lead_id=lead_id, proposta_id=item.proposta_id, action=action,
                issue_key=issue_key, status="ok" if message is None else "error", message=message
            ))
        except Exception as e:
            logging.error(f"Erro inesperado ao processar lead {lead_id}: {e}", exc_info=True)
            results.append(SendResult(
                lead_id=lead_id, proposta_id=item.proposta_id, action="fatal_error",
                status="error", message=str(e)
            ))
    return {"results": results}

APP_DIR = os.path.dirname(os.path.abspath(__file__))
FRONTEND_DIR = os.path.normpath(os.path.join(APP_DIR, "..", "frontend"))

@app.post("/api/sync-scheduled")
async def sync_scheduled(
    background_tasks: BackgroundTasks,
    date_from: str = Query(...),
    date_to: str = Query(...),
    fornecedor: str = Query(...)
):
    # Agenda a tarefa para rodar "atrás das cortinas"
    background_tasks.add_task(process_sync, date_from, date_to, fornecedor)
    return {"status": "accepted", "message": f"Sincronizacao de {fornecedor} iniciada em background."}


@app.get("/", response_class=FileResponse, include_in_schema=False)
async def read_index():
    index_path = os.path.join(FRONTEND_DIR, 'index.html')
    if not os.path.exists(index_path):
        raise HTTPException(status_code=404, detail="index.html não encontrado")
    return FileResponse(index_path)

app.mount("/", StaticFiles(directory=FRONTEND_DIR, html=False), name="static_root")

@app.get("/{full_path:path}", response_class=FileResponse, include_in_schema=False)
async def catch_all(full_path: str):
    if full_path.startswith("api/"): raise HTTPException(status_code=404, detail="Not Found")
    index_path = os.path.join(FRONTEND_DIR, 'index.html')
    if not os.path.exists(index_path): raise HTTPException(status_code=404, detail="index.html não encontrado")
    return FileResponse(index_path)

async def process_sync(date_from: str, date_to: str, fornecedor: str):
    try:
        logging.info(f"Sync iniciado: {fornecedor} de {date_from} ate {date_to}")
        # 1. Busca no FileMaker [cite: 1]
        leads = fm_client.get_leads_with_proposals(date_from, date_to, fornecedor)

        if not leads:
            logging.info("Nenhum lead encontrado para este periodo.")
            return

        # 2. Prepara o payload para a mesma lógica do /api/send [cite: 2]
        items = [SendItem(**item) for item in leads]
        payload = SendPayload(items=items, fornecedor=fornecedor)

        # 3. Chama a função de envio para o Jira [cite: 2]
        # Aqui você pode simplesmente chamar a lógica que já existe no seu post("/api/send")
        await send_to_jira(payload)
        logging.info(f"Sync finalizado para {fornecedor}")
    except Exception as e:
        logging.error(f"Erro no processamento em background: {e}")


