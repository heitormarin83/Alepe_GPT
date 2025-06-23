import requests
from datetime import datetime
import yagmail
import os
from dotenv import load_dotenv

load_dotenv()

EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_APP_PASSWORD = os.getenv("EMAIL_APP_PASSWORD")
EMAIL_RECIPIENT = os.getenv("EMAIL_RECIPIENT")


def consultar_proposicao(proposicao, numero, ano):
    logs = []
    logs.append("🚀 Iniciando captura via API da ALEPE")

    url = f"https://dadosabertos.alepe.pe.gov.br/api/v1/proposicoes/{proposicao}/?numero={numero}&ano={ano}"
    logs.append(f"🔗 Acessando API: {url}")

    try:
        response = requests.get(url, timeout=60)
        logs.append(f"📥 Status da resposta: {response.status_code}")

        if response.status_code != 200:
            logs.append(f"❌ Erro na captura: Status {response.status_code}")
            return {"erro": f"Status {response.status_code}", "logs": logs}

        if not response.content:
            logs.append("⚠️ Resposta vazia da API.")
            return {"erro": "Resposta vazia", "logs": logs}

        try:
            dados = response.json()
        except Exception as e:
            logs.append(f"❌ Erro ao converter JSON: {e}")
            return {"erro": "JSON inválido", "logs": logs}

        if not dados:
            logs.append("⚠️ Nenhum dado encontrado para essa proposição.")
            return {"erro": "Nenhum dado encontrado", "logs": logs}

        logs.append("✅ Dados capturados com sucesso")
        return {"dados": dados, "logs": logs}

    except Exception as e:
        logs.append(f"❌ Erro na captura: {e}")
        return {"erro": str(e), "logs": logs}


def enviar_email(assunto, conteudo, logs):
    try:
        yag = yagmail.SMTP(EMAIL_USER, EMAIL_APP_PASSWORD)
        yag.send(
            to=EMAIL_RECIPIENT,
            subject=assunto,
            contents=[conteudo, "\n\nLogs:\n" + "\n".join(logs)]
        )
        print("✅ E-mail enviado com sucesso!")
    except Exception as e:
        print(f"❌ Erro ao enviar e-mail: {e}")


def executar_robot(proposicao, numero, ano):
    print("🚀 Iniciando execução do Alepe_GPT com API")
    resultado = consultar_proposicao(proposicao, numero, ano)

    if 'erro' in resultado:
        assunto = f"[ERRO] Alepe GPT - {datetime.now().strftime('%d/%m/%Y')}"
        enviar_email(assunto, "❌ Erro na execução", resultado['logs'])
        return {"status": "erro", "logs": resultado['logs']}

    dados = resultado['dados']
    texto_email = f"""
    <h2>Resultado da Proposição {numero}/{ano}</h2>
    <pre>{dados}</pre>
    """

    assunto = f"Acompanhamento ALEPE - {proposicao.upper()} {numero}/{ano} - {datetime.now().strftime('%d/%m/%Y')}"
    enviar_email(assunto, texto_email, resultado['logs'])

    return {"status": "sucesso", "dados": dados, "logs": resultado['logs']}


if __name__ == "__main__":
    # 🔥 Teste com dados válidos
    resultado = executar_robot("projetos", "1", "2023")
    print(resultado)
