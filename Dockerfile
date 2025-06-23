FROM mcr.microsoft.com/playwright/python:v1.52.0-jammy

WORKDIR /app

COPY . /app

# Instala dependências de sistema necessárias para o Chromium do Playwright
RUN apt-get update && apt-get install -y \
    libnss3 \
    libatk-bridge2.0-0 \
    libgtk-3-0 \
    libx11-xcb1 \
    libxcomposite1 \
    libxdamage1 \
    libxrandr2 \
    libxfixes3 \
    libc6 \
    libxext6 \
    libx11-6 \
    libasound2 \
    libxkbcommon0 \
    libgbm1 \
    && rm -rf /var/lib/apt/lists/*

# Instala dependências Python
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Instala navegadores do Playwright
RUN playwright install

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]

