import requests
from datetime import datetime
import yagmail
import os
from dotenv import load_dotenv

load_dotenv()

EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_APP_PASSWORD = os.getenv("EMAIL_APP_PASSWORD")
EMAIL_RECIPIENT = os.getenv("EMAIL_RECIPIENT")
DOCID = os.getenv("DOCID")


def consultar_api_alepe(docid):
    logs = []
    logs.append("🚀 Iniciando captura via API da ALEPE")

    url = f"https://www.alepe.pe.gov.br/wp-json/alepe/v1/proposicoes/{docid}"
    logs.append(f"🔗 Acessando: {url}")

    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()

        dados = response.json()

        titulo = dados.get("tipo", "Título não encontrado") + " " + dados.get("numero", "") + "/" + dados.get("ano", "")
        ementa = dados.get("ementa", "Ementa não encontrada")
        situacao = dados.get("situacao", "Situação não encontrada")
        data_apresentacao = dados.get("data_apresentacao", "Data não encontrada")

        logs.append("✅ Dados capturados com sucesso")

        return {
            "titulo": titulo,
            "ementa": ementa,
            "situacao": situacao,
            "data_apresentacao": data_apresentacao,
            "url": url,
            "log": logs
        }

    except Exception as e:
        erro = f"❌ Erro na captura: {e}"
        logs.append(erro)
        return {"erro": erro, "log": logs}


def gerar_template_email(dados):
    agora = datetime.now().strftime('%d/%m/%Y %H:%M:%S')

    html = f"""
    <div style="font-family:Arial; color:#333;">
        <h2 style="color:#004b87;">{dados['titulo']}</h2>
        <p><strong>Ementa:</strong><br>{dados['ementa']}</p>
        <p><strong>Situação:</strong> {dados['situacao']}</p>
        <p><strong>Data de Apresentação:</strong> {dados['data_apresentacao']}</p>
        <hr>
        <p>
            <small>Consulta realizada em {agora} | 
            <a href="{dados['url']}" target="_blank">Acessar Proposição</a></small>
        </p>
    </div>
    """
    return html


def enviar_email(assunto, corpo_html, logs):
    try:
        yag = yagmail.SMTP(EMAIL_USER, EMAIL_APP_PASSWORD)
        yag.send(
            to=EMAIL_RECIPIENT,
            subject=assunto,
            contents=[corpo_html, "\n\nLogs:\n" + "\n".join(logs)]
        )
        print("✅ E-mail enviado com sucesso!")
    except Exception as e:
        print(f"❌ Erro ao enviar e-mail: {e}")


def executar_robot(docid=None):
    print("🚀 Iniciando execução do Alepe_GPT com API")
    docid = docid or DOCID

    if not docid:
        erro = "❌ DOCID não definido na função ou no .env"
        print(erro)
        return {"status": "erro", "logs": [erro]}

    dados = consultar_api_alepe(docid)

    if 'erro' in dados:
        assunto = f"[ERRO] Alepe GPT - {datetime.now().strftime('%d/%m/%Y')}"
        enviar_email(assunto, "❌ Erro na execução", dados.get('log', []))
        return {"status": "erro", "logs": dados['log']}

    corpo_email = gerar_template_email(dados)
    assunto = f"Acompanhamento ALEPE - {dados['titulo']} - {datetime.now().strftime('%d/%m/%Y')}"
    enviar_email(assunto, corpo_email, dados['log'])
    return {"status": "sucesso", "dados": dados, "logs": dados['log']}


if __name__ == "__main__":
    resultado = executar_robot()
    print(resultado)


if __name__ == "__main__":
    resultado = executar_robot()
    print(resultado)
