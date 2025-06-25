# Usa imagem leve
FROM python:3.10-slim

# Define diretório de trabalho
WORKDIR /app

# Copia todo o projeto
COPY . /app

# Instala apenas o que for necessário
RUN pip install --upgrade pip \
 && pip install -r requirements.txt

# Expõe a porta (padrão 8000) — será sobrescrita pelo Railway em $PORT
ENV PORT=${PORT:-8000}
EXPOSE ${PORT}

# Usa shell form para interpolar a variável $PORT
CMD ["sh", "-c", "uvicorn app:app --host 0.0.0.0 --port $PORT"]
