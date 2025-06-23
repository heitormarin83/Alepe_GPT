# Alepe GPT Monitor

Um robô que consulta proposições no site da Alepe e envia e-mail diário com as atualizações.

## Como usar no Railway

1. Crie um projeto Railway conectado ao seu GitHub.
2. Configure as variáveis de ambiente:
   - EMAIL_USER
   - EMAIL_APP_PASSWORD (Senha de aplicativo do Gmail)
   - EMAIL_RECIPIENT
   - DOCID (Ex: 15016)
   - TIPOPROP (Ex: p)
3. Clique em Deploy.

## Cron Job

- Configure um cron job na aba Plugins para rodar diariamente:
