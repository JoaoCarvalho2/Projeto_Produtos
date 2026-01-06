Integração FileMaker → Jira (Leads e Propostas)

Este projeto é uma aplicação full stack (FastAPI + HTML/CSS/JS) criada para integrar Leads e Propostas do FileMaker com o Jira, permitindo que usuários filtrem registros por período e fornecedor, visualizem os dados em uma interface web e sincronizem tudo com o Jira de forma automatizada e confiável.

O sistema foi projetado para evitar duplicidades, garantir consistência dos dados e enriquecer as issues do Jira com informações detalhadas de produtos e follow-ups vindas do FileMaker.

🚀 Funcionalidades Principais
🔎 Busca e Visualização

Filtro por intervalo de datas.

Filtro dinâmico por fornecedor/fabricante (ex: Atlassian, AnyDesk, SonarQube).

Busca automática de:

Leads no FileMaker.

Proposta mais recente associada a cada Lead.

Visualização dos dados em tabela interativa no frontend.

📤 Envio Inteligente para o Jira

Verificação automática de issues existentes no Jira pelo ID do Lead.

Nova lógica de sincronização:

Se a issue já existir → ela é deletada e recriada.

Garante que o Jira sempre reflita o estado mais atual do FileMaker.

Criação de issues do tipo Lead no projeto configurado.

🧠 Mapeamento Avançado de Campos

Conversão de valores textuais do FileMaker para IDs de campos customizados do Jira.

Mapeamentos centralizados no arquivo mappings.py:

Status

País

Categoria

Vendedor

Criação automática de opções de campos select-list no Jira, caso não existam.

💬 Comentários Automáticos (Novo)

Após criar a issue, o sistema adiciona comentários estruturados contendo:

📦 Produtos da proposta, com valores individuais.

💰 Valor total da proposta.

📝 Follow-ups históricos, com data, usuário e descrição.

Comentários são enviados usando o formato ADF (Atlassian Document Format).

📊 Interface Web

Seleção individual ou em massa de registros.

Contadores de itens selecionados.

Exportação dos dados selecionados para CSV.

Feedback visual em tempo real:

✅ Sucesso (com link direto para a issue no Jira).

❌ Erro detalhado por item.

🧱 Arquitetura do Projeto
joaocarvalho2-projeto_produtos/
├── README.md
├── backend/
│   ├── app.py              # API FastAPI e orquestração geral
│   ├── fm_client.py        # Integração com FileMaker Data API
│   ├── jira_client.py      # Integração completa com Jira REST API
│   ├── mappings.py         # Mapeamento FileMaker → Jira
│   └── requirements.txt
└── frontend/
    ├── index.html          # Interface web
    ├── script.js           # Lógica frontend (fetch, UI, envios)
    └── style.css           # Estilos

🛠️ Tech Stack
Backend

Python 3.8+

FastAPI

Uvicorn

Requests

python-dotenv

Frontend

HTML5

CSS3

JavaScript (Vanilla ES6+)

Integrações

FileMaker Data API

Jira REST API v3

🔄 Fluxo de Funcionamento

Usuário seleciona datas e fornecedor no frontend.

Frontend chama GET /api/leads.

Backend:

Autentica no FileMaker.

Busca Leads.

Busca a proposta mais recente de cada Lead.

Usuário seleciona os itens desejados.

Frontend envia os dados via POST /api/send.

Backend:

Procura issue existente no Jira pelo ID do Lead.

Se existir → deleta a issue.

Cria uma nova issue.

Atualiza campos customizados.

Adiciona comentários com produtos e follow-ups.

Frontend exibe o status final de cada item.

⚙️ Configuração
Pré-requisitos

Python 3.8+

Acesso à API do FileMaker

Conta no Jira com permissões de criação/edição

Token de API do Jira

Campos customizados já criados no Jira

Instalação
git clone <url-do-repositorio>
cd joaocarvalho2-projeto_produtos
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r backend/requirements.txt

Variáveis de Ambiente (.env)
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


API disponível em:
http://127.0.0.1:8000

Frontend

Abra o arquivo frontend/index.html diretamente no navegador.

📌 Observações Importantes

Os IDs de customfield_XXXXX são específicos da instância do Jira.

Revise e ajuste:

mappings.py

jira_client.py

A lógica de delete + recreate foi adotada para evitar inconsistências históricas.
