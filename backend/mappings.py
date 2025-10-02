# Mapeamentos de campos para conversão de valores do FileMaker para IDs do Jira

status_map = {
    "Proposta": "10142", "Em Andamento": "10143", "Aprovado": "10144",
    "Fechado": "10145", "Cancelado": "10139", "Cotação": "10146"
}
pais_map = {
    "Brasil": "10131", "Colômbia": "10417", "México": "10133",
    "EUA": "10134", "Panama": "13778", "Guatemala": "14016"
}
vendedor_map = {
  "Arthur Pontes Vieira": "16108", "Felipe Guerreiro": "16110", "Demetrius Rego Leal": "16112",
  "Karen Cristina Silva Costa": "16113", "Bruno Caliope Plachi": "16114", "Alex Fernando de Sousa": "16115",
  "Felipi Costa Massarão": "16116", "Ana Maria De Assis": "16117", "Felipe Santos Pedro": "16118",
  "Erivan Andrade Junior": "16120", "Daniel Ferreira Macario": "16122", "Rafael Citro": "16123",
  "Ana Carolina Vitor Belo": "16124", "Ketlyn Soares Pereira": "16125", "Lucas R. B. Santos": "16126",
  "Maria Silvia Lourençato Tremarin": "16127", "Filipi Alves Jacob": "16128", "Ana Carolina Belo": "16133",
  "Mario Cesar Machado": "16134", "Gabriel Messias de Melo": "16137", "Ana Paula Mendes de Oliveira": "16138",
  "Renato C Costa": "16139", "Gabriela dos Santos Brito": "16140", "Daniel Sete Rufino": "16141",
  "Kauê Machado Vasconcellos": "16142", "Andreia Trindade Barga": "16143", "Jessica Danielle de Sousa Barbosa": "16144",
  "Silvia Cainelli": "16145", "Angel Sanchez": "16146", "Jefferson Garrido Salgado": "16164",
  "Beatriz Correa Alves e Silva": "16168", "Ana Carolina De Jesus Gonçalves Moura": "16173", "Lorena Cuevas Gomez": "16174",
  "Felipe Pereira da Silva": "16175", "Juan Valentín Alvarez Salcedo": "16176", "Erivan Andrade": "16177",
  "Leonardo de Souza Dias Machado": "16178", "Flavio Luiz Miranda Ribeiro": "16179", "Marcio de Almeida": "16180",
  "Saúl Garcia Juárez": "16181", "Selma Cassia Dias de Oliveira Barata": "16182", "Julio Felix": "16183",
  "Amanda dos Santos Dezidera": "16184", "Gerson Dias": "16185", "Cauê Thiago dos Santos": "16186",
  "Beatriz Eriksson de Carvalho": "16187", "Beatriz Ferraraccio Bolsoni": "16188", "Key Account Enterprise I": "16189",
  "David Garcia Juarez": "16190", "Laura Barbosa Correia Santana": "16191", "Juliana Tavares de Paula": "16192",
  "Fabio Dias Dunga": "16193", "Vinicius Rodrigues Silva": "16194", "Valter Gabriel Silva Oliveira": "16195",
  "Artur de Sá Rodrigues": "16196", "Alex F. S.": "16197", "Olga Lucia Delgado": "16198",
  "Areli Sanchez": "16199", "Luis Guilherme Pinto": "16200", "Saúl G. Juárez": "16201",
  "Glauber Vitor Da Cruz": "16202", "Dayana Alejandra Avila Machuca": "16203", "Alan Gimaque Rodrigues da Silva": "16207",
  "Carlos Eduardo dos Santos Assis": "16218", "Anderson Dalbo": "16219", "Lucas Ricard Brito Santos": "16224",
  "Mayara Alves do Nascimento": "16365", "Carlos Eduardo Del Busso Albano": "16372"
}
categoria_map = {
    "AGRONEGOCIO": "10153", "AUTARQUIA": "10605", "Comercial": "10122", "Corporativo": "10119",
    "Educacional": "10159", "ENERGIA/OLEO/GAS": "10422", "Financeiro": "10144", "Governo": "10118",
    "HEALTHCARE": "10161", "INDUSTRIA": "10440", "INTEGRADORES DE TECNOLOGIA": "10603",
    "LOGISTICA/TRANSPORTE": "10606", "Pessoa Física": "10120", "Revenda": "10121",
    "SERVICOS": "10447", "VAREJO": "10165", "PESSOA FISICA": "14897", "PF": "14912", "Educativo": "15338"
}
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