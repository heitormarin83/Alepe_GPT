import requests
from datetime import datetime
import yagmail
import os
import json
from dotenv import load_dotenv

# Carrega variáveis de ambiente
load_dotenv()

EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_APP_PASSWORD = os.getenv("EMAIL_APP_PASSWORD")
EMAIL_RECIPIENT = os.getenv("EMAIL_RECIPIENT")

PROPOSICAO = os.getenv("PROPOSICAO") or "projetos"
NUMERO = os.getenv("NUMERO") or "3005"
ANO = os.getenv("ANO") or "2025"

# Arquivo para armazenar o histórico anterior
DATA_FILE = "dados_anteriores.json"


def consultar_proposicao(proposicao, numero, ano):
    logs = []
    logs.append("🚀 Iniciando captura via API da ALEPE")

    url = f"https://dadosabertos.alepe.pe.gov.br/api/v1/proposicoes/{proposicao}/?numero={numero}&ano={ano}"
    logs.append(f"🔗 Acessando API: {url}")

    try:
        response = requests.get(url, timeout=60, headers={"Accept": "application/json"})
        logs.append(f"📥 Status da resposta: {response.status_code}")

        if response.status_code != 200:
            logs.append(f"❌ Erro na API: {response.status_code} - {response.text}")
            return {"erro": f"API retornou status {response.status_code}", "logs": logs}

        if not response.text.strip():
            logs.append("⚠️ Resposta vazia da API.")
            return {"erro": "Resposta vazia", "logs": logs}

        try:
            data = response.json()
        except Exception as e:
            logs.append(f"❌ Erro ao converter JSON: {e}")
            logs.append(f"📝 Conteúdo retornado: {response.text}")
            return {"erro": "JSON inválido ou resposta fora do padrão", "logs": logs}

        if not data:
            logs.append("⚠️ Nenhum dado encontrado para essa proposição.")
            return {"erro": "Nenhum dado encontrado", "logs": logs}

        logs.append("✅ Dados capturados com sucesso")
        return {"dados": data, "logs": logs}

    except Exception as e:
        logs.append(f"❌ Erro na requisição: {e}")
        return {"erro": str(e), "logs": logs}


def extrair_dados(dados):
    historico = dados.get("historico", "Histórico não encontrado")
    info = (
        dados.get("informacoes_complementares")
        or dados.get("informacoesComplementares")
        or "Informações complementares não encontradas"
    )
    return historico.strip(), info.strip()


def carregar_dados_anteriores():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"historico": "", "info_complementar": ""}


def salvar_dados_atuais(historico, info_complementar):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(
            {"historico": historico.strip(), "info_complementar": info_complementar.strip()},
            f,
            ensure_ascii=False,
            indent=4,
        )


def comparar(atual, anterior):
    return atual.strip() != anterior.strip()


def gerar_template_email(historico, info_complementar):
    agora = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
    historico_html = historico.replace("\n", "<br>")
    info_html = info_complementar.replace("\n", "<br>")

    return f"""
    <div style="font-family:Arial; color:#333;">
        <h2 style="color:#004b87;">Histórico</h2>
        <p>{historico_html}</p>
        <hr>
        <h2 style="color:#004b87;">Informações Complementares</h2>
        <p>{info_html}</p>
        <hr>
        <p><small>Consulta realizada em {agora}</small></p>
    </div>
    """


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


def executar_robot():
    print("🚀 Iniciando execução do Alepe_GPT com API")
    resultado = consultar_proposicao(PROPOSICAO, NUMERO, ANO)

    if 'erro' in resultado:
        assunto = f"[ERRO] Alepe GPT - {datetime.now().strftime('%d/%m/%Y')}"
        enviar_email(assunto, "❌ Erro na execução", resultado['logs'])
        return {"status": "erro", "logs": resultado['logs']}

    dados = resultado['dados']
    historico, info = extrair_dados(dados)

    anteriores = carregar_dados_anteriores()

    mudou_historico = comparar(historico, anteriores.get("historico", ""))
    mudou_info = comparar(info, anteriores.get("info_complementar", ""))

    salvar_dados_atuais(historico, info)

    status_emoji = "🟥" if mudou_historico or mudou_info else "🟩"
    data_hoje = datetime.now().strftime('%d/%m/%Y')
    assunto = f"Status ALEPE - {NUMERO}/{ANO} - {data_hoje} {status_emoji}"

    corpo = gerar_template_email(historico, info)
    enviar_email(assunto, corpo, resultado['logs'])

    return {
        "status": "sucesso",
        "mudou_historico": mudou_historico,
        "mudou_info": mudou_info,
        "logs": resultado['logs']
    }


if __name__ == "__main__":
    executar_robot()


if __name__ == "__main__":
    resultado = executar_robot("projetos", "3005", "2025")
    print(resultado)
