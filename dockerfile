FROM mcr.microsoft.com/playwright/python:v1.52.0-jammy

WORKDIR /app

COPY . /app

# Instala dependências de sistema (pode ser opcional com --with-deps, mas não atrapalha deixar)
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
    libx11-6 \
    libxcb1 \
    libxtst6 \
    libasound2 \
    libgbm1 \
    libxkbcommon0 \
    && rm -rf /var/lib/apt/lists/*

# Instala dependências Python
RUN pip install --upgrade pip --no-cache-dir
RUN pip install -r requirements.txt --no-cache-dir

# 🔥 Aqui está a chave para funcionar:
RUN playwright install --with-deps

EXPOSE 8000

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
