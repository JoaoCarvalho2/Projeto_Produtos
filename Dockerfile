# [Arquivo: Dockerfile]

# 1. Imagem base
FROM python:3.10-slim

# 2. Define o diretório de trabalho
WORKDIR /app

# 3. Copia SÓ o requirements.txt primeiro (para otimizar o cache)
COPY backend/requirements.txt .
# 4. Instala as dependências
RUN pip install --no-cache-dir -r requirements.txt

# --- ADICIONE ESTA LINHA ---
# Copia o .env da raiz do projeto (host) para /app/.env (container)
COPY .env .
# ---------------------------

# 5. Copia as duas pastas inteiras para dentro do container
COPY backend/ /app/backend/
COPY frontend/ /app/frontend/

# 6. Expõe a porta que o Gunicorn usará
EXPOSE 8000

# 7. Comando para iniciar o servidor
CMD ["gunicorn", "-w", "8", "-k", "uvicorn.workers.UvicornWorker", "backend.app:app", "-b", "0.0.0.0:8000", "--timeout", "200"]