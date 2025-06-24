import requests
from datetime import datetime
import yagmail
import os
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_APP_PASSWORD = os.getenv("EMAIL_APP_PASSWORD")
EMAIL_RECIPIENT = os.getenv("EMAIL_RECIPIENT")

# Arquivos para armazenar o histórico anterior
HISTORICO_FILE = "historico_anterior.txt"
INFO_COMP_FILE = "info_complementar_anterior.txt"


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

        if 'application/json' not in response.headers.get('Content-Type', ''):
            logs.append(f"❌ Conteúdo não é JSON: {response.text}")
            return {"erro": "Resposta não é JSON", "logs": logs}

        data = response.json()

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
    info = dados.get("informacoes_complementares", "Informações complementares não encontradas")
    return historico.strip(), info.strip()


def comparar_conteudo(atual, anterior):
    return atual.strip() != anterior.strip()


def gerar_template_email(historico, info_complementar):
    agora = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
    historico_formatado = historico.replace("\n", "<br>")
    info_formatado = info_complementar.replace("\n", "<br>")

    html = f"""
    <div style="font-family:Arial;">
        <h2 style="color:#004b87;">Histórico</h2>
        <p>{historico_formatado}</p>
        <hr>
        <h2 style="color:#004b87;">Informações Complementares</h2>
        <p>{info_formatado}</p>
        <hr>
        <p><small>Consulta realizada em {agora}</small></p>
    </div>
    """
    return html


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


def carregar_dado_anterior(arquivo):
    if os.path.exists(arquivo):
        with open(arquivo, "r", encoding="utf-8") as f:
            return f.read().strip()
    return ""


def salvar_dado_atual(arquivo, conteudo):
    with open(arquivo, "w", encoding="utf-8") as f:
        f.write(conteudo.strip())


def executar_robot(proposicao, numero, ano):
    print("🚀 Iniciando execução do Alepe_GPT com API")
    resultado = consultar_proposicao(proposicao, numero, ano)

    if 'erro' in resultado:
        assunto = f"[ERRO] Alepe GPT - {datetime.now().strftime('%d/%m/%Y')}"
        enviar_email(assunto, "❌ Erro na execução", resultado['logs'])
        return {"status": "erro", "logs": resultado['logs']}

    dados = resultado['dados']
    historico, info = extrair_dados(dados)

    historico_anterior = carregar_dado_anterior(HISTORICO_FILE)
    info_anterior = carregar_dado_anterior(INFO_COMP_FILE)

    mudou_historico = comparar_conteudo(historico, historico_anterior)
    mudou_info = comparar_conteudo(info, info_anterior)

    salvar_dado_atual(HISTORICO_FILE, historico)
    salvar_dado_atual(INFO_COMP_FILE, info)

    status = "🟥" if (mudou_historico or mudou_info) else "🟩"
    data_hoje = datetime.now().strftime('%d/%m/%Y')
    assunto = f"Status ALEPE - {numero}/{ano} - {data_hoje} {status}"

    corpo = gerar_template_email(historico, info)

    enviar_email(assunto, corpo, resultado['logs'])

    return {
        "status": "sucesso",
        "mudou_historico": mudou_historico,
        "mudou_info": mudou_info,
        "logs": resultado['logs']
    }


if __name__ == "__main__":
    executar_robot("projetos", "3005", "2025")


