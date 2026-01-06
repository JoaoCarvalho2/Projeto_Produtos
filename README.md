# Integração FileMaker → Jira (Leads e Propostas)

Este projeto é uma aplicação **full stack** containerizada (FastAPI + HTML/CSS/JS + Docker) responsável por integrar **Leads, Propostas e Follow-ups do FileMaker** com o **Jira**, permitindo consulta, filtragem, visualização e sincronização automatizada de dados entre as plataformas.

O sistema garante **consistência total**, evitando duplicidades por meio da estratégia de **exclusão e recriação de issues**, além de enriquecer o Jira com comentários estruturados, histórico de follow-ups e dados financeiros das propostas.

---

## 🚀 Funcionalidades

### 🔎 Consulta e Filtros
- Filtro por **intervalo de datas**
- Filtro por **fornecedor/fabricante** (Atlassian, Anydesk, SonarQube)
- Busca automática de:
  - Leads no FileMaker
  - Proposta mais recente vinculada ao Lead
  - Follow-ups associados à proposta
- Visualização em tabela interativa no frontend

### 📊 Interface Web Avançada
- Seleção individual ou em massa
- Seleção automática apenas de itens **com valor > 0**
- Busca local por:
  - Empresa
  - Contato
  - ID do Lead
- Filtro local por **faixa de valores**
- Contadores dinâmicos
- Exportação dos registros selecionados para **CSV**
- Feedback visual por linha (sucesso / erro)
- Link direto para a issue criada no Jira

### 📤 Integração com Jira
- Busca de issues existentes pelo **ID do Lead**
- Estratégia de sincronização:
  - Issue existente → **deletada**
  - Nova issue criada com dados atualizados
- Criação de issues do tipo **Lead**
- Preenchimento automático de:
  - Campos customizados
  - Datas normalizadas
  - Valores financeiros
  - Produto (via mapeamento inteligente por palavra-chave)

### 💬 Comentários Automáticos (ADF)
- Inclusão automática de comentários no padrão **Atlassian Document Format**
- Conteúdo dos comentários:
  - Produtos e valor da proposta
  - Histórico completo de follow-ups
  - Painel informativo em caso de fallback

### 🧠 Mapeamentos Inteligentes
- Conversão de valores textuais do FileMaker para **IDs de campos do Jira**
- Mapeamentos centralizados em `mappings.py`:
  - Status
  - País
  - Categoria
  - Vendedor
  - Email do vendedor
  - Produto (match parcial por nome)
- Criação automática de opções em campos *select-list* do Jira quando necessário

### ⚙️ Processamento em Background
- Endpoint para **sincronização agendada**
- Execução assíncrona usando `BackgroundTasks`
- Reutiliza a mesma lógica do envio manual

---

## 🧱 Estrutura do Projeto
joaocarvalho2-projeto_produtos/
├── Dockerfile
├── backend/
│ ├── app.py # API FastAPI e orquestração
│ ├── fm_client.py # Integração com FileMaker Data API
│ ├── jira_client.py # Integração com Jira REST API
│ ├── mappings.py # Mapeamentos FileMaker → Jira
│ └── requirements.txt
└── frontend/
├── index.html # Interface web
├── script.js # Lógica frontend
└── style.css # Estilos


---

## 🛠️ Tech Stack

### Backend
- Python 3.10
- FastAPI
- Uvicorn
- Gunicorn
- Requests
- python-dotenv

### Frontend
- HTML5
- CSS3
- JavaScript (Vanilla ES6+)

### Infra
- Docker
- Dockerfile otimizado com cache de dependências

### Integrações
- FileMaker Data API (vLatest)
- Jira REST API v3

---

## 🔄 Fluxo de Funcionamento

1. Usuário acessa a interface web
2. Aplica filtros de data e fornecedor
3. Frontend chama `GET /api/leads`
4. Backend:
   - Autentica no FileMaker
   - Busca Leads
   - Busca proposta mais recente
   - Busca follow-ups
5. Usuário seleciona registros
6. Frontend envia dados via `POST /api/send`
7. Backend:
   - Procura issue existente no Jira
   - Deleta se existir
   - Cria nova issue
   - Atualiza campos customizados
   - Adiciona comentários estruturados
8. Frontend exibe status final por item

---

## ⚙️ Endpoints Principais

### `GET /api/leads`
Busca Leads com Propostas e Follow-ups  
**Parâmetros:**
- `date_from` (YYYY-MM-DD)
- `date_to` (YYYY-MM-DD)
- `fornecedor`

### `POST /api/send`
Envia os Leads selecionados para o Jira

### `POST /api/sync-scheduled`
Dispara sincronização em background  
**Parâmetros:**
- `date_from`
- `date_to`
- `fornecedor`

---

## 🐳 Docker

### Build da imagem
```bash
docker build -t fm-jira-integrator .
```
Execução
docker run -p 8000:8000 --env-file .env fm-jira-integrator
Aplicação disponível em:
http://localhost:8000

🔐 Variáveis de Ambiente (.env)
# Jira
JIRA_URL=https://suaempresa.atlassian.net
JIRA_EMAIL=seu-email@empresa.com
JIRA_API_TOKEN=seu_token
JIRA_CLIENTE_CONTEXT_ID=12330
JIRA_PROJECT_KEY_ATLASSIAN=ATL
JIRA_PROJECT_KEY_ANYDESK=ANY
JIRA_PROJECT_KEY_SONARQUBE=SON

# FileMaker
FM_HOST=servidor.fm.com
FM_DATABASE=Banco
FM_USER=usuario
FM_PASSWORD=senha
FM_LAYOUT_LEAD=dados_lead_api
FM_LAYOUT_PROPOSTA=dados_proposta_api
FM_LAYOUT_FOLLOW=dados_follow_api
FM_PROPOSAL_LINK_FIELD=lead.proposta::id
FM_FOLLOW_LINK_FIELD=id_proposta

# SSL
DISABLE_SSL_VERIFY=false

⚠️ Observações Importantes

Os IDs customfield_XXXXX são específicos da instância do Jira

Ajuste os mapeamentos em mappings.py conforme seu ambiente

A estratégia de delete + recreate garante sincronização fiel

Existe fallback automático para salvar dados na descrição se houver bloqueio de tela no Jira
