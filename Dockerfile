# Imagem atualizada do Playwright com Python e browsers
FROM mcr.microsoft.com/playwright/python:v1.52.0-jammy

# Diretório de trabalho
WORKDIR /app

# Copiar arquivos do projeto
COPY . /app

# Instalar dependências do Python
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Comando padrão
CMD ["python", "main.py"]
