# Integração FileMaker → Jira (Leads e Propostas)

Este projeto é uma aplicação **full stack** (FastAPI + HTML/CSS/JS) criada para integrar **Leads e Propostas do FileMaker** com o **Jira**, permitindo que usuários filtrem registros por período e fornecedor, visualizem os dados em uma interface web e sincronizem tudo com o Jira de forma automatizada e confiável.

O sistema foi projetado para evitar duplicidades, garantir consistência dos dados e enriquecer as issues do Jira com **informações detalhadas de produtos e follow-ups** vindas do FileMaker.

---

## 🚀 Funcionalidades Principais

### 🔎 Busca e Visualização
- Filtro por **intervalo de datas**
- Filtro dinâmico por **fornecedor/fabricante** (Atlassian, AnyDesk, SonarQube)
- Busca automática de:
  - Leads no FileMaker
  - Proposta mais recente associada a cada Lead
- Visualização dos dados em tabela interativa

### 📤 Envio Inteligente para o Jira
- Verificação automática de issues existentes pelo **ID do Lead**
- **Nova lógica de sincronização**:
  - Issue existente → **deletada e recriada**
  - Garante dados sempre atualizados no Jira
- Criação de issues do tipo **Lead**

### 🧠 Mapeamento Avançado
- Conversão de valores do FileMaker para **IDs de campos customizados**
- Mapeamentos centralizados em `mappings.py`
- Criação automática de opções em campos *select-list* no Jira

### 💬 Comentários Automáticos
- Inclusão automática de comentários com:
  - 📦 Produtos da proposta
  - 💰 Valor total da proposta
  - 📝 Histórico de follow-ups
- Comentários no padrão **ADF (Atlassian Document Format)**

### 📊 Interface Web
- Seleção individual ou em massa
- Contadores dinâmicos
- Exportação para **CSV**
- Feedback visual em tempo real com link direto para a issue

---

## 🧱 Estrutura do Projeto

joaocarvalho2-projeto_produtos/
├── README.md
├── backend/
│ ├── app.py
│ ├── fm_client.py
│ ├── jira_client.py
│ ├── mappings.py
│ └── requirements.txt
└── frontend/
├── index.html
├── script.js
└── style.css


---

## 🛠️ Tech Stack

### Backend
- Python 3.8+
- FastAPI
- Uvicorn
- Requests
- python-dotenv

### Frontend
- HTML5
- CSS3
- JavaScript (Vanilla ES6+)

### Integrações
- FileMaker Data API
- Jira REST API v3

---

## 🔄 Fluxo de Funcionamento

1. Usuário filtra por datas e fornecedor
2. Frontend chama `GET /api/leads`
3. Backend busca Leads e Propostas no FileMaker
4. Usuário seleciona os registros
5. Frontend envia via `POST /api/send`
6. Backend:
   - Busca issue pelo ID do Lead
   - Deleta se existir
   - Cria nova issue
   - Atualiza campos
   - Adiciona comentários
7. Frontend exibe status final

---

## ⚙️ Configuração

### Pré-requisitos
- Python 3.8+
- Acesso à API do FileMaker
- Conta no Jira com permissões
- Token de API do Jira
- Campos customizados configurados no Jira

### Instalação

```bash
git clone <url-do-repositorio>
cd joaocarvalho2-projeto_produtos
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r backend/requirements.txt
```
🔐 Variáveis de Ambiente (.env)
# Jira
JIRA_URL=https://suaempresa.atlassian.net
JIRA_EMAIL=seu-email@empresa.com
JIRA_API_TOKEN=seu_token
JIRA_PROJECT_KEY=PROJ
JIRA_CLIENTE_CONTEXT_ID=10150

# FileMaker
FM_HOST=servidor.fm.com
FM_DATABASE=Banco
FM_USER=usuario
FM_PASSWORD=senha
FM_LAYOUT_LEAD=LayoutLeads
FM_LAYOUT_PROPOSTA=LayoutPropostas
FM_PROPOSAL_LINK_FIELD=lead.proposta::id

▶️ Como Executar

Backend
cd backend
uvicorn app:app --reload

API: http://127.0.0.1:8000

Frontend

Abra frontend/index.html no navegador

⚠️ Observações Importantes

IDs customfield_XXXXX são específicos da instância do Jira

Ajuste mappings.py e jira_client.py conforme seu ambiente

Estratégia de delete + recreate garante consistência total dos dados

A versão com docker roda como API podendo evitar a necessidade do front-end e automatizar o processo e a versão sendo utilizada.
