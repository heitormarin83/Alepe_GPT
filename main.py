import requests
import yagmail
from datetime import datetime
import os
import json
from dotenv import load_dotenv

load_dotenv()

# Variáveis de ambiente
EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASSWORD = os.getenv("EMAIL_APP_PASSWORD")
EMAIL_RECIPIENT = os.getenv("EMAIL_RECIPIENT")

# Dados da proposição
TIPO = "projetos"
NUMERO = "3005"
ANO = "2025"

# Arquivo para armazenar o último status
ARQUIVO_STATUS = "status_anterior.json"


def buscar_dados_alepe():
    url = f"https://dadosabertos.alepe.pe.gov.br/api/v1/proposicoes/{TIPO}/?numero={NUMERO}&ano={ANO}"
    logs = []
    logs.append(f"🔗 Acessando API: {url}")

    try:
        response = requests.get(url, timeout=60)
        logs.append(f"📥 Status da resposta: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            if isinstance(data, list) and data:
                item = data[0]
                historico = item.get("historico", "Histórico não encontrado")
                informacoes = item.get("informacoes_complementares", "Informações complementares não encontradas")
                return historico, informacoes, logs
            else:
                logs.append("❌ Dados não encontrados na resposta.")
                return None, None, logs
        else:
            logs.append(f"❌ Erro HTTP: {response.status_code}")
            return None, None, logs

    except Exception as e:
        logs.append(f"❌ Erro na requisição: {e}")
        return None, None, logs


def carregar_status_anterior():
    if os.path.exists(ARQUIVO_STATUS):
        with open(ARQUIVO_STATUS, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"historico": "", "informacoes": ""}


def salvar_status_atual(historico, informacoes):
    with open(ARQUIVO_STATUS, "w", encoding="utf-8") as f:
        json.dump({"historico": historico, "informacoes": informacoes}, f, ensure_ascii=False, indent=4)


def gerar_corpo_email(historico, informacoes):
    historico_formatado = historico.replace("\n", "<br>")
    informacoes_formatado = informacoes.replace("\n", "<br>")

    html = f"""
    <div style="font-family:Arial; color:#333;">
        <h2 style="color:#004b87;">Histórico</h2>
        <p>{historico_formatado}</p>
        <hr>
        <h2 style="color:#004b87;">Informações Complementares</h2>
        <p>{informacoes_formatado}</p>
    </div>
    """
    return html


def enviar_email(status, corpo_html, logs):
    hoje = datetime.now().strftime('%d/%m/%Y')
    icone = "🟢" if status == "sem_alteracao" else "🔴"
    assunto = f"{icone} Status ALEPE - 3005/2025 - {hoje}"

    try:
        yag = yagmail.SMTP(EMAIL_USER, EMAIL_PASSWORD)
        yag.send(
            to=EMAIL_RECIPIENT,
            subject=assunto,
            contents=[corpo_html, "\n\nLogs:\n" + "\n".join(logs)]
        )
        print("✅ E-mail enviado com sucesso!")
    except Exception as e:
        print(f"❌ Erro ao enviar e-mail: {e}")


def executar_robot():
    print("🚀 Iniciando execução do Alepe_GPT")

    historico, informacoes, logs = buscar_dados_alepe()

    if not historico or not informacoes:
        logs.append("❌ Erro ao obter dados da API.")
        enviar_email("erro", "<h3>❌ Erro na execução</h3>", logs)
        return {"status": "erro", "logs": logs}

    status_anterior = carregar_status_anterior()

    houve_alteracao = (
        historico != status_anterior.get("historico") or
        informacoes != status_anterior.get("informacoes")
    )

    status = "alterado" if houve_alteracao else "sem_alteracao"

    corpo = gerar_corpo_email(historico, informacoes)

    enviar_email(status, corpo, logs)

    salvar_status_atual(historico, informacoes)

    return {"status": status, "logs": logs}


if __name__ == "__main__":
    resultado = executar_robot()
    print(resultado)
