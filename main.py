import requests
from datetime import datetime
import yagmail
import os
from dotenv import load_dotenv

# Carrega variáveis de ambiente
load_dotenv()
EMAIL_USER         = os.getenv("EMAIL_USER")
EMAIL_APP_PASSWORD = os.getenv("EMAIL_APP_PASSWORD")
EMAIL_RECIPIENT    = os.getenv("EMAIL_RECIPIENT")

# Arquivos locais para armazenar o histórico e info complementar do dia anterior
HISTORICO_FILE     = "historico_anterior.txt"
INFO_COMP_FILE     = "info_complementar_anterior.txt"


def consultar_proposicao(proposicao, numero, ano):
    logs = ["🚀 Iniciando captura via API da ALEPE"]
    url  = f"https://dadosabertos.alepe.pe.gov.br/api/v1/proposicoes/{proposicao}/?numero={numero}&ano={ano}"
    logs.append(f"🔗 Acessando API: {url}")

    try:
        resp = requests.get(url, timeout=60, headers={"Accept": "application/json"})
        logs.append(f"📥 Status da resposta: {resp.status_code}")

        if resp.status_code != 200:
            logs.append(f"❌ API retornou status {resp.status_code}")
            return {"erro":"Status != 200","logs":logs}

        if not resp.content.strip():
            logs.append("⚠️ Resposta vazia")
            return {"erro":"Resposta vazia","logs":logs}

        try:
            data = resp.json()
        except Exception as e:
            logs.append(f"❌ JSON inválido: {e}")
            logs.append(f"📝 Texto: {resp.text}")
            return {"erro":"JSON inválido","logs":logs}

        if not data:
            logs.append("⚠️ Sem dados")
            return {"erro":"Sem dados","logs":logs}

        logs.append("✅ Dados capturados com sucesso")
        return {"dados":data, "logs":logs}

    except Exception as e:
        logs.append(f"❌ Erro na requisição: {e}")
        return {"erro":str(e), "logs":logs}


def extrair_dados(dados):
    # Extraímos exatamente os campos que interessam
    historico = dados.get("historico", "")
    info      = dados.get("informacoes_complementares", "")
    return historico.strip(), info.strip()


def carregar_anterior(path):
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return f.read().strip()
    return ""


def salvar_atual(path, texto):
    with open(path, "w", encoding="utf-8") as f:
        f.write(texto.strip())


def teve_alteracao(atual, anterior):
    return atual != anterior


def gerar_html(historico, info):
    agora = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
    h = historico.replace("\n","<br>")
    i = info.replace("\n","<br>")
    return f"""
    <div style="font-family:Arial;">
      <h2 style="color:#004b87;">Histórico</h2>
      <p>{h}</p><hr>
      <h2 style="color:#004b87;">Informações Complementares</h2>
      <p>{i}</p><hr>
      <p><small>Em {agora}</small></p>
    </div>
    """


def enviar_email(assunto, corpo_html, logs):
    yag = yagmail.SMTP(EMAIL_USER, EMAIL_APP_PASSWORD)
    yag.send(
        to=EMAIL_RECIPIENT,
        subject=assunto,
        contents=[corpo_html, "\n\nLogs:\n" + "\n".join(logs)]
    )
    print("📧 Email enviado")


def executar_robot(proposicao, numero, ano):
    print("🚀 Iniciando execução com API")
    r = consultar_proposicao(proposicao, numero, ano)
    if 'erro' in r:
        assunto = f"[ERRO] Alepe GPT - {datetime.now().strftime('%d/%m/%Y')}"
        enviar_email(assunto, "❌ Erro na execução", r['logs'])
        return {"status":"erro","logs":r['logs']}

    dados = r['dados']
    h_atual, info_atual = extrair_dados(dados)

    # lê o que tínhamos ontem
    h_ant = carregar_anterior(HISTORICO_FILE)
    i_ant = carregar_anterior(INFO_COMP_FILE)

    muda_h = teve_alteracao(h_atual, h_ant)
    muda_i = teve_alteracao(info_atual, i_ant)

    # salva para amanhã
    salvar_atual(HISTORICO_FILE, h_atual)
    salvar_atual(INFO_COMP_FILE, info_atual)

    # monta status
    status = "🟥" if (muda_h or muda_i) else "🟩"
    assunto = f"Status ALEPE - {numero}/{ano} - {datetime.now().strftime('%d/%m/%Y')} {status}"

    # corpo
    html = gerar_html(h_atual, info_atual)
    enviar_email(assunto, html, r['logs'])

    return {"status":"sucesso","muda_historico":muda_h,"muda_info":muda_i}


if __name__ == "__main__":
    resultado = executar_robot("projetos","3005","2025")
    print(resultado)

