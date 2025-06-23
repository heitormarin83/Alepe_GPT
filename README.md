# Alepe GPT Robot

Robo para capturar dados de proposições na ALEPE e enviar por e-mail.

## Funcionalidades:
- 🔥 Envio de logs no corpo do e-mail.
- 🔥 Loop de debug para Railway.
- 🔥 API via FastAPI com endpoints:
  - `/` → Status
  - `/run` → Executa o robô manualmente

## Como rodar no Railway:
1. Configure as variáveis de ambiente:
   - EMAIL_USER
   - EMAIL_APP_PASSWORD
   - EMAIL_RECIPIENT
   - DOCID
   - TIPOPROP
2. Deploy direto do GitHub com Dockerfile.

## Comandos:
- Container sobe rodando uma API FastAPI.
- Ou roda automaticamente pelo `main.py` com o loop de debug.
