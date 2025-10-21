Integração FileMaker para Jira
Este é um projeto de aplicação web full-stack (FastAPI + Vanilla JS) que serve como uma ferramenta de integração entre o FileMaker e o Jira.

A aplicação permite que usuários busquem por Leads e Propostas no FileMaker dentro de um intervalo de datas específico, selecionem os registros desejados em uma interface web e os enviem para o Jira. O backend processa cada item e, de forma inteligente, cria uma nova Issue no Jira ou atualiza uma Issue existente caso ela já tenha sido enviada anteriormente.

Funcionalidades Principais
Interface Web: Frontend simples para filtrar Leads por data, visualizar e selecionar resultados.

Busca no FileMaker: Conecta-se à API de Dados do FileMaker para buscar Leads (filtrando pelo fabricante "Atlassian") e suas respectivas Propostas mais recentes.

Sincronização Inteligente: Para cada Lead enviado, o sistema primeiro verifica no Jira (usando um campo customizado para o ID do Lead) se uma Issue já existe.

Se existir: Atualiza a Issue com os dados mais recentes do FileMaker.

Se não existir: Cria uma nova Issue no projeto Jira configurado.

Mapeamento de Dados: Utiliza um arquivo de mapeamento (mappings.py) para converter valores de texto do FileMaker (como "Brasil", "Em Andamento", "Nome do Vendedor") para os IDs correspondentes nos campos customizados do Jira.

Feedback em Tempo Real: A interface web atualiza o status de cada item enviado, mostrando "Sucesso" (com um link direto para a Issue no Jira) ou "Erro".

Exportação: Permite exportar os itens selecionados para um arquivo CSV.

Tech Stack
Backend: Python 3.8+

FastAPI: Para a criação da API REST.

Requests: Para realizar chamadas às APIs do FileMaker e Jira.

python-dotenv: Para gerenciamento de variáveis de ambiente.

Frontend:

HTML5

CSS3 (Moderno, com variáveis)

JavaScript (Vanilla JS, ES6+), usando fetch para chamadas de API.

Servidor:

Uvicorn: Como servidor ASGI para o FastAPI.

Arquitetura e Fluxo de Dados
Usuário (Frontend): O usuário abre o index.html, seleciona um intervalo de datas e clica em "Buscar".

API (Backend): O script.js chama o endpoint GET /api/leads no app.py (FastAPI).

FileMaker (Backend): O app.py usa o fm_client.py para: a. Autenticar e obter um token da API de Dados do FileMaker. b. Executar uma busca no layout de Leads (FM_LAYOUT_LEAD) pelo intervalo de datas e fabricante == "Atlassian". c. Para cada Lead encontrado, executa uma segunda busca no layout de Propostas (FM_LAYOUT_PROPOSTA) para encontrar a proposta mais recente (ordenando por ID descendente).

API (Backend): O app.py formata os dados e os retorna como um JSON para o frontend.

Usuário (Frontend): O script.js recebe o JSON, renderiza a tabela de resultados e habilita o botão de envio.

Usuário (Frontend): O usuário seleciona os itens e clica em "Enviar Selecionados para Jira".

API (Backend): O script.js chama o endpoint POST /api/send com um payload contendo os dados dos itens selecionados.

Jira (Backend): Para cada item no payload, o app.py usa o jira_client.py para: a. Chamar find_issue_by_lead_id() para buscar no Jira por uma Issue que já tenha o ID do Lead (ex: cf[10132] ~ "LEAD_ID"). b. Mapear os campos do FileMaker para o formato do Jira usando o _map_fields() e os dicionários em mappings.py. c. Se a Issue for encontrada, chama update_issue() (requisição PUT). d. Se não for encontrada, chama create_and_update_issue() (requisição POST seguida de PUT para preencher todos os campos).

API (Backend): O app.py compila os resultados (sucesso/erro, issue key) e os retorna ao frontend.

Usuário (Frontend): O script.js atualiza o status de cada linha da tabela, mostrando o link do Jira em caso de sucesso ou uma mensagem de erro.

Configuração e Instalação
Para rodar este projeto, você precisa configurar as credenciais do FileMaker e do Jira, além de ajustar os mapeamentos de campos.

1. Pré-requisitos
Python 3.8 ou superior.

Acesso à API de Dados do FileMaker com um usuário e senha.

Uma conta do Jira com permissão para criar/editar Issues e um Token de API.

Um projeto no Jira com os campos customizados necessários (para ID do Lead, Vendedor, País, etc.).

2. Instalação
Clone este repositório:

Bash

git clone <url-do-seu-repositorio>
cd <nome-do-repositorio>
Crie e ative um ambiente virtual (recomendado):

Bash

python -m venv venv
source venv/bin/activate  # No Windows: venv\Scripts\activate
Instale as dependências Python:

Bash

pip install fastapi "uvicorn[standard]" requests python-dotenv
(Você pode querer criar um requirements.txt com esses pacotes)

3. Variáveis de Ambiente (.env)
Crie um arquivo chamado .env na raiz do projeto e preencha com as suas credenciais. Use o jira_client.py e fm_client.py como referência para todas as variáveis necessárias.

Ini, TOML

# --- Configuração do Jira ---
JIRA_URL="https://suaempresa.atlassian.net"
JIRA_EMAIL="seu-email@dominio.com"
JIRA_API_TOKEN="SeuTokenDeAPIDoJira"
JIRA_PROJECT_KEY="PROJ"

# --- Configuração do FileMaker ---
FM_HOST="fm.seuservidor.com"
FM_DATABASE="NomeDoBanco"
FM_USER="usuario_api"
FM_PASSWORD="senha_api"
FM_LAYOUT_LEAD="LayoutDeLeads"
FM_LAYOUT_PROPOSTA="LayoutDePropostas"
FM_PROPOSAL_LINK_FIELD="lead.proposta::id" # Campo que liga a proposta ao lead

# (Opcional) Desabilitar verificação SSL (não recomendado para produção)
# DISABLE_SSL_VERIFY="true"
4. Mapeamento de Campos (IMPORTANTE)
O arquivo mappings.py traduz dados do FileMaker para os IDs do Jira. Os IDs no arquivo (10142, 16108, etc.) são específicos da sua instância do Jira.

Você DEVE atualizar este arquivo com os IDs corretos da sua instância:

status_map: Mapeia o status do Lead (ex: "Proposta") para o ID da Opção do campo no Jira.

pais_map: Mapeia o nome do país para o ID da Opção.

vendedor_map: Mapeia o nome do vendedor para o ID do Usuário ou Opção no Jira.

categoria_map: Mapeia a categoria para o ID da Opção.

vendedor_email_map: Mapeia o nome do vendedor para o e-mail (usado em campos de usuário).

Como encontrar os IDs no Jira:

Para campos de Opção (Select List): Vá em Configurações > Issues > Campos Customizados, encontre o campo, clique em "Contextos e valor padrão" (ou "Options") e inspecione os IDs.

Para Usuários: O vendedor_map parece usar IDs de Opções (como um "Assistente de Vendas"), não de usuários. Verifique se o seu campo customfield_10146 é um campo de usuário ou de seleção.

5. IDs de Campos Customizados (IMPORTANTE)
O arquivo jira_client.py possui IDs de campos customizados (ex: customfield_10132, customfield_10151) fixos no código, principalmente no método _map_fields.

Você DEVE inspecionar o seu Jira e atualizar todos os customfield_XXXXX para que correspondam aos campos da sua instância.

Principalmente:

cf[10132] em find_issue_by_lead_id(): Este é o campo que armazena o ID do Lead do FileMaker. Ele é crucial para a lógica de "atualizar vs. criar".

Como Usar
Iniciar o Backend: No seu terminal, com o ambiente virtual ativado, rode o Uvicorn:

Bash

uvicorn app:app --reload
O servidor estará rodando em http://127.0.0.1:8000.

Abrir o Frontend: Abra o arquivo index.html diretamente no seu navegador (ex: clicando duas vezes nele).

Buscar Leads:

Selecione a "Data Início" e "Data Fim".

Clique em "Buscar (Apenas Atlassian)".

A tabela será preenchida com os resultados.

Enviar para o Jira:

Marque os checkboxes dos itens que deseja enviar.

Use "Selecionar Tudo" ou "Desselecionar Tudo" para facilitar.

Clique no botão "Enviar Selecionados para Jira".

Confirme o envio na janela modal.

Verificar Resultados:

Aguarde o processamento. A coluna "Status Envio" será atualizada.

Sucesso: A linha ficará verde e mostrará um link para a Issue criada/atualizada no Jira.

Erro: A linha ficará vermelha. Passe o mouse sobre a mensagem de erro para ver mais detalhes (se disponíveis).
