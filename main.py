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
PROPOSICAO = os.getenv("PROPOSICAO", "projetos")
NUMERO = os.getenv("NUMERO", "3005")
ANO = os.getenv("ANO", "2025")

# Arquivos locais para armazenar os dados do dia anterior
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
            logs.append(f"❌ A resposta não é JSON. Content-Type: {response.headers.get('Content-Type')}")
            return {"erro": "Resposta não é JSON", "logs": logs}

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
    info = dados.get("informacoes_complementares", "Informações complementares não encontradas")
    return historico.strip(), info.strip()


def comparar_e_obter_status(atual, anterior):
    return atual.strip() != anterior.strip()


def gerar_template_email(historico, info_complementar):
    agora = datetime.now().strftime('%d/%m/%Y %H:%M:%S')

    historico_formatado = historico.replace("\n", "<br>")
    info_formatado = info_complementar.replace("\n", "<br>")

    html = f"""
    <div style="font-family:Arial; color:#333;">
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

    if 'erro' in res

