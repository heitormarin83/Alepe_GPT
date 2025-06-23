import requests
from requests.exceptions import HTTPError
from dotenv import load_dotenv
import yagmail
import os
from datetime import datetime

load_dotenv()

EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_APP_PASSWORD = os.getenv("EMAIL_APP_PASSWORD")
EMAIL_RECIPIENT = os.getenv("EMAIL_RECIPIENT")
DOCID = os.getenv("DOCID")
TIPOPROP = os.getenv("TIPOPROP")


def consultar_proposicao_api(docid, tipoprop):
    logs = []
    logs.append("🚀 Iniciando captura via API da ALEPE")

    url = f"https://www.alepe.pe.gov.br/wp-json/alepe/v1/proposicoes/{docid}"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "application/json",
    }

    logs.append(f"🔗 Acessando API da ALEPE para docid={docid} e tipoprop={tipoprop}")

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()

        data = response.json()

        titulo = data.get('titulo', 'Título não encontrado')
        ementa = data.get('ementa', 'Ementa não encontrada')
        historico = data.get('historico', 'Histórico não encontrado')
        info_complementar = data.get('informacoesComplementares', 'Informações Complementares não encontradas')

        logs.append("✅ Dados capturados com sucesso via API")
        return {
            "titulo": titulo,
            "ementa": ementa,
            "historico": historico,
            "info_complementar": info_complementar,
            "url": url,
            "log": logs
        }

    except HTTPError as http_err:
        logs.append(f"❌ Erro HTTP: {http_err}")
        return {"erro": str(http_err), "log": logs}

    except Exception as err:
        logs.append(f"❌ Erro geral na captura: {err}")
        return {"erro": str(err), "log": logs}


def enviar_email(assunto, corpo, logs):
    try:
        yag = yagmail.SMTP(EMAIL_USER, EMAIL_APP_PASSWORD)
        yag.send(
            to=EMAIL_RECIPIENT,
            subject=assunto,
            contents=[corpo, "\n\nLogs:\n" + "\n".join(logs)]
        )
        print("✅ E-mail enviado com sucesso")
    except Exception as e:
        print(f"❌ Erro ao enviar e-mail: {e}")


def executar_robot(docid=None, tipoprop=None):
    print("🚀 Iniciando execução do Alepe_GPT via API")

    docid = docid or DOCID
    tipoprop = tipoprop or TIPOPROP

    if not docid or not tipoprop:
        erro = "❌ DOCID ou TIPOPROP não definidos na função ou no .env"
        print(erro)
        return {"status": "erro", "logs": [erro]}

    dados = consultar_proposicao_api(docid, tipoprop)

    if 'erro' in dados:
        assunto = f"[ERRO] Alepe GPT - {datetime.now().strftime('%d/%m/%Y')}"
        enviar_email(assunto, "❌ Erro na execução", dados.get('log', []))
        return {"status": "erro", "logs": dados['log']}

    assunto = f"Acompanhamento ALEPE - {dados['titulo']} - {datetime.now().strftime('%d/%m/%Y')}"
    corpo = f"""
Título: {dados['titulo']}
Ementa: {dados['ementa']}
Histórico: {dados['historico']}
Informações Complementares: {dados['info_complementar']}
Link: {dados['url']}
"""
    enviar_email(assunto, corpo, dados['log'])
    return {"status": "sucesso", "dados": dados, "logs": dados['log']}


if __name__ == "__main__":
    resultado = executar_robot()
    print(resultado)
