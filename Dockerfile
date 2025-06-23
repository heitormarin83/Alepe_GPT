# Imagem base com suporte para Playwright
FROM mcr.microsoft.com/playwright/python:v1.52.0-jammy

# Setar diretório de trabalho
WORKDIR /app

# Copiar tudo para dentro do container
COPY . /app

# Instalar dependências do Python
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Comando padrão
CMD ["python", "main.py"]
