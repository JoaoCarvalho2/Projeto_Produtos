# Mapeamentos de campos para conversão de valores do FileMaker para IDs do Jira

# Adicione isso ao final do arquivo, ou junto com os outros maps
# mappings.py

# Mapa de palavras-chave -> ID Genérico no Jira
produtos_map = {
    # Se o nome tiver "Jira", usa este ID (Ex: 17128 é [ Jira] no seu log)
    "Jira": "17128",       
    
    # Se o nome tiver "Confluence", usa este ID (Ex: 17051 é [Confluence])
    "Confluence": "17051", 
    
    # Se o nome tiver "Bitbucket", usa este ID (Ex: 17032 é [Bitbucket])
    "Bitbucket": "17032",
    
    # Se o nome tiver "Trello", usa este ID (Ex: 17243 é [Trello])
    "Trello": "17243"      
}


status_map = {
    "Proposta": "16981", "Em Andamento": "17754", "Aprovado": "17755",
    "Fechado": "17756", "Cancelado": "16977", "Cotação": "16978"
}
pais_map = {
    "Brasil": "16105", "Colômbia": "16106", "México": "16111",
    "EUA": "16107", "Panama": "16110", "Guatemala": "16108",
    "Argentina": "12247", "Venezuela": "12248", "Mexico": "16109"
}
vendedor_map = {
  "Arthur Pontes Vieira": "17613", "Felipe Guerreiro": "17614", "Demetrius Rego Leal": "17615",
  "Karen Cristina Silva Costa": "17616", "Bruno Caliope Plachi": "17617", "Alex Fernando de Sousa": "17618",
  "Felipi Costa Massarão": "17619", "Ana Maria De Assis": "17620", "Felipe Santos Pedro": "17621",
  "Erivan Andrade Junior": "17622", "Daniel Ferreira Macario": "17623", "Rafael Citro": "17624",
  "Ana Carolina Vitor Belo": "17625", "Ketlyn Soares Pereira": "17626", "Lucas R. B. Santos": "17627",
  "Maria Silvia Lourençato Tremarin": "17628", "Filipi Alves Jacob": "17629", "Ana Carolina Belo": "17630",
  "Mario Cesar Machado": "17631", "Gabriel Messias de Melo": "17632", "Ana Paula Mendes de Oliveira": "17633",
  "Renato C Costa": "17634", "Gabriela dos Santos Brito": "17635", "Daniel Sete Rufino": "17636",
  "Kauê Machado Vasconcellos": "17637", "Andreia Trindade Barga": "17638", "Jessica Danielle de Sousa Barbosa": "17639",
  "Silvia Cainelli": "17640", "Angel Sanchez": "17641", "Jefferson Garrido Salgado": "17642",
  "Beatriz Correa Alves e Silva": "17643", "Ana Carolina De Jesus Gonçalves Moura": "17644",
  "Lorena Cuevas Gomez": "17645", "Felipe Pereira da Silva": "17646", "Juan Valentín Alvarez Salcedo": "17647",
  "Erivan Andrade": "17648", "Leonardo de Souza Dias Machado": "17649", "Flavio Luiz Miranda Ribeiro": "17650",
  "Marcio de Almeida": "17651", "Saúl Garcia Juárez": "17652", "Selma Cassia Dias de Oliveira Barata": "17653",
  "Julio Felix": "17654", "Amanda dos Santos Dezidera": "17655", "Gerson Dias": "17656",
  "Cauê Thiago dos Santos": "17657", "Beatriz Eriksson de Carvalho": "17658",
  "Beatriz Ferraraccio Bolsoni": "17659", "Key Account Enterprise I": "17660",
  "David Garcia Juarez": "17661", "Laura Barbosa Correia Santana": "17662", "Juliana Tavares de Paula": "17663",
  "Fabio Dias Dunga": "17664", "Vinicius Rodrigues Silva": "17665", "Valter Gabriel Silva Oliveira": "17666",
  "Artur de Sá Rodrigues": "17667", "Alex F. S.": "17668", "Olga Lucia Delgado": "17669",
  "Areli Sanchez": "17670", "Luis Guilherme Pinto": "17671", "Saúl G. Juárez": "17672",
  "Glauber Vitor Da Cruz": "17673", "Dayana Alejandra Avila Machuca": "17674",
  "Alan Gimaque Rodrigues da Silva": "17675", "Carlos Eduardo dos Santos Assis": "17676",
  "Anderson Dalbo": "17677", "Lucas Ricard Brito Santos": "17678",
  "Mayara Alves do Nascimento": "17679", "Carlos Eduardo Del Busso Albano": "17680"
};

categoria_map = {
  "AGRONEGOCIO": "16050",
  "AUTARQUIA": "16051",
  "Comercial": "16052",
  "Corporativo": "16053",
  "Educacional": "16054",
  "ENERGIA/OLEO/GAS": "16055",
  "Financeiro": "16056",
  "Governo": "16057",
  "HEALTHCARE": "16058",
  "INDUSTRIA": "16059",
  "INTEGRADORES DE TECNOLOGIA": "16060",
  "LOGISTICA/TRANSPORTE": "16061",
  "Pessoa Física": "16062",
  "Revenda": "16063",
  "SERVICOS": "16064",
  "VAREJO": "16065",
  "PESSOA FISICA": "16066",
  "PF": "16067",
  "Educativo": "16068",
  "Jira": "16069",
  "Jira Premium": "16070",
  "Trello - Premium": "16071",
  "Professional Services": "16072"
};

vendedor_email_map = {
    "Arthur Pontes Vieira": "arthur.souza@software.com.br", "Felipe Guerreiro": "felipe.teixeira@software.com.br",
    "Demetrius Rego Leal": "demetrius.leal@software.com.br", "Karen Cristina Silva Costa": "karen.costa@software.com.br",
    "Bruno Caliope Plachi": "bruno.caliope@software.com.br", "Alex Fernando de Sousa": "alex.fernando@software.com.br",
    "Felipi Costa Massarão": "felipi.costa@software.com.br", "Ana Maria De Assis": "ana.assis@software.com.br",
    "Felipe Santos Pedro": "felipe.santos@software.com.br", "Erivan Andrade Junior": "felipe.santos@software.com.br",
    "Daniel Ferreira Macario": "daniel.macario@software.com.br", "Rafael Citro": "rafael.citro@software.com.br",
    "Ana Carolina Vitor Belo": "carolina.belo@software.com.br", "Ketlyn Soares Pereira": "ketlyn.soares@software.com.br",
    "Lucas R. B. Santos": "lucas.santos@software.com.br", "Maria Silvia Lourençato Tremarin": "silvia.lourencato@software.com.br",
    "Filipi Alves Jacob": "filipi.jacob@software.com.br", "Ana Carolina Belo": "carolina.belo@software.com.br",
    "Mario Cesar Machado": "mario.machado@software.com.br", "Gabriel Messias de Melo": "gabriel.melo@software.com.br",
    "Ana Paula Mendes de Oliveira": "ana.mendes@software.com.br", "Renato C Costa": "renato.costa@software.com.br",
    "Gabriela dos Santos Brito": "gabriela.brito@software.com.br", "Daniel Sete Rufino": "daniel.rufino@software.com.br",
    "Kauê Machado Vasconcellos": "kaue.machado@software.com.br", "Andreia Trindade Barga": "andreia.barga@software.com.br",
    "Jessica Danielle de Sousa Barbosa": "jessica.barbosa@software.com.br", "Silvia Cainelli": "silvia.cainelli@software.com.br",
    "Angel Sanchez": "angel.sanchez@software.com.mx", "Jefferson Garrido Salgado": "jefferson.garrido@software.com.br",
    "Beatriz Correa Alves e Silva": "beatriz.silva@software.com.br", "Ana Carolina De Jesus Gonçalves Moura": "ana.moura@software.com.br",
    "Lorena Cuevas Gomez": "lorena.cuevas@software.com.mx", "Felipe Pereira da Silva": "felipe.pereira@software.com.br",
    "Juan Valentín Alvarez Salcedo": "juan.salcedo@software.com.co", "Erivan Andrade": "erivanj@software.com.br",
    "Leonardo de Souza Dias Machado": "leonardo.machado@software.com.br", "Flavio Luiz Miranda Ribeiro": "kaue.machado@software.com.br",
    "Marcio de Almeida": "marcio.almeida@software.com.br", "Saúl Garcia Juárez": "saul.garcia@software.com.mx",
    "Selma Cassia Dias de Oliveira Barata": "selma.oliveira@software.com.br", "Julio Felix": "juliof@software.com.br",
    "Amanda dos Santos Dezidera": "amanda.dezidera@software.com.br", "Gerson Dias": "gerson.dias@software.com.br",
    "Cauê Thiago dos Santos": "caue.santos@software.com.br", "Beatriz Eriksson de Carvalho": "beatriz.carvalho@software.com.br",
    "Beatriz Ferraraccio Bolsoni": "beatriz.bolsoni@software.com.br", "David Garcia Juarez": "david.garcia@software.com.mx",
    "Laura Barbosa Correia Santana": "laura.santana@software.com.br", "Juliana Tavares de Paula": "juliana.tavares@software.com.br",
    "Fabio Dias Dunga": "fabio.dunga@software.com.br", "Vinicius Rodrigues Silva": "vinicius.silva@software.com.br",
    "Valter Gabriel Silva Oliveira": "valter.gabriel@software.com.br", "Artur de Sá Rodrigues": "artur.rodrigues@software.com.br",
    "Alex F. S.": "alex.fernando@software.com.br", "Olga Lucia Delgado": "olga@software.com.co",
    "Areli Sanchez": "areli@software.com.mx", "Luis Guilherme Pinto": "luis.guilherme@software.com.br",
    "Glauber Vitor Da Cruz": "glauber.cruz@software.com.br", "Dayana Alejandra Avila Machuca": "dayana.avila@software.com.co",
    "Alan Gimaque Rodrigues da Silva": "alan.silva@software.com.br", "Carlos Eduardo dos Santos Assis": "eduardo.assis@software.com.br",
    "Anderson Dalbo": "anderson.dalbo@software.com.br", "Lucas Ricard Brito Santos": "lucas.santos@software.com.br",
    "Mayara Alves do Nascimento": "mayara@boxware.com.br", "Carlos Eduardo Del Busso Albano": "carlos.eduardo@boxware.com.br"
}