import os
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from datetime import datetime
import yagmail
from dotenv import load_dotenv

# Carrega variáveis de ambiente
load_dotenv()
EMAIL_USER         = os.getenv("EMAIL_USER")
EMAIL_APP_PASSWORD = os.getenv("EMAIL_APP_PASSWORD")
EMAIL_RECIPIENT    = os.getenv("EMAIL_RECIPIENT")

def montar_session_com_retries(
    total_retries=5,
    backoff_factor=1,
    status_forcelist=None
):
    """
    Cria uma Session com retry tanto no connect quanto no read,
    para respostas 429 e 5xx, e também retry em ConnectTimeout.
    """
    status_forcelist = status_forcelist or [429, 500, 502, 503, 504]
    retry = Retry(
        total=total_retries,
        connect=total_retries,
        read=total_retries,
        backoff_factor=backoff_factor,
        status_forcelist=status_forcelist,
        allowed_methods=["GET"],
        raise_on_status=False,
        raise_on_redirect=False
    )
    sess = requests.Session()
    adapter = HTTPAdapter(max_retries=retry)
    sess.mount("http://", adapter)
    sess.mount("https://", adapter)
    return sess

def consultar_proposicao(proposicao, numero, ano):
    logs = ["🚀 Iniciando captura via API da ALEPE"]
    url = f"https://dadosabertos.alepe.pe.gov.br/api/v1/proposicoes/{proposicao}/?numero={numero}&ano={ano}"
    logs.append(f"🔗 GET {url}")

    sess = montar_session_com_retries()
    try:
        # timeout=(connect_timeout, read_timeout)
        resp = sess.get(url, timeout=(30, 60), headers={
            "Accept": "application/json",
            "User-Agent": "Mozilla/5.0 (compatible; AlepeBot/1.0)"
        })
        logs.append(f"📥 HTTP {resp.status_code}")

        if resp.status_code != 200:
            logs.append(f"❌ API retornou {resp.status_code}: {resp.text[:200]}…")
            return {"erro": f"HTTP {resp.status_code}", "logs": logs}

        if not resp.text.strip():
            logs.append("⚠️ Resposta vazia")
            return {"erro": "vazio", "logs": logs}

        try:
            data = resp.json()
        except Exception as e:
            logs.append(f"❌ Falha no JSON: {e}")
            logs.append(f"📝 Preview texto: {resp.text[:200]}…")
            return {"erro": "json", "logs": logs}

        logs.append("✅ JSON OK")
        return {"dados": data, "logs": logs}

    except requests.exceptions.ConnectTimeout:
        logs.append("❌ ConnectTimeout")
        return {"erro": "ConnectTimeout", "logs": logs}
    except requests.exceptions.ReadTimeout:
        logs.append("❌ ReadTimeout")
        return {"erro": "ReadTimeout", "logs": logs}
    except Exception as e:
        logs.append(f"❌ Erro inesperado: {e}")
        return {"erro": str(e), "logs": logs}

def extrair_dados(dados):
    hist = dados.get("historico", "")
    info = dados.get("informacoes_complementares", "")
    return hist.strip(), info.strip()

def gerar_template_email(historico, info):
    agora = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    h = historico.replace("\n", "<br>")
    i = info.replace("\n", "<br>")
    return f"""
    <div style="font-family:Arial,sans-serif; color:#333;">
      <h2 style="color:#004b87;">Histórico</h2>
      <p>{h or "<i>(vazio)</i>"}</p><hr>
      <h2 style="color:#004b87;">Informações Complementares</h2>
      <p>{i or "<i>(vazio)</i>"}</p><hr>
      <p><small>Consulta em {agora}</small></p>
    </div>
    """

def enviar_email(assunto, corpo, logs):
    yag = yagmail.SMTP(EMAIL_USER, EMAIL_APP_PASSWORD)
    yag.send(
        to=EMAIL_RECIPIENT,
        subject=assunto,
        contents=[corpo, "\n\nLogs:\n" + "\n".join(logs)]
    )
    print("✅ E-mail enviado")

def executar_robot(proposicao, numero, ano):
    print("🚀 Executando Alepe_GPT")
    res = consultar_proposicao(proposicao, numero, ano)
    if "erro" in res:
        assunto = f"[ERRO] ALEPE – {datetime.now():%d/%m/%Y}"
        enviar_email(assunto, "<p>❌ Falha na execução</p>", res["logs"])
        return {"status": "erro", "logs": res["logs"]}

    hist, info = extrair_dados(res["dados"])
    assunto = f"Atualização ALEPE – {numero}/{ano} – {datetime.now():%d/%m/%Y}"
    corpo   = gerar_template_email(hist, info)
    enviar_email(assunto, corpo, res["logs"])
    return {"status": "sucesso"}

if __name__ == "__main__":
    out = executar_robot("projetos", "3005", "2025")
    print(out)


