import os
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from datetime import datetime
import yagmail
from dotenv import load_dotenv

# Carrega variáveis de ambiente
load_dotenv()
EMAIL_USER          = os.getenv("EMAIL_USER")
EMAIL_APP_PASSWORD  = os.getenv("EMAIL_APP_PASSWORD")
EMAIL_RECIPIENT     = os.getenv("EMAIL_RECIPIENT")

def montar_session_com_retries(retries=3, backoff=1, status_forcelist=None):
    """Cria uma session com retry e backoff para GETs."""
    session = requests.Session()
    retry = Retry(
        total=retries,
        backoff_factor=backoff,
        status_forcelist=status_forcelist or [429, 500, 502, 503, 504],
        allowed_methods=["GET"],
        raise_on_status=False,
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount("https://", adapter)
    session.mount("http://", adapter)
    return session

def consultar_proposicao(proposicao, numero, ano):
    logs = ["🚀 Iniciando captura via API da ALEPE"]
    url = f"https://dadosabertos.alepe.pe.gov.br/api/v1/proposicoes/{proposicao}/?numero={numero}&ano={ano}"
    logs.append(f"🔗 GET {url}")

    session = montar_session_com_retries(retries=5, backoff=1)
    try:
        resp = session.get(url, timeout=(10, 20), headers={"Accept": "application/json"})
        logs.append(f"📥 Status HTTP: {resp.status_code}")

        if resp.status_code != 200:
            logs.append(f"❌ API retornou {resp.status_code}: {resp.text}")
            return {"erro": f"HTTP {resp.status_code}", "logs": logs}

        if not resp.text.strip():
            logs.append("⚠️ Corpo vazio")
            return {"erro": "Resposta vazia", "logs": logs}

        try:
            data = resp.json()
        except Exception as e:
            logs.append(f"❌ JSON inválido: {e}")
            logs.append(f"📝 Preview: {resp.text[:200]}…")
            return {"erro": "JSON inválido", "logs": logs}

        logs.append("✅ Dados válidos recebidos")
        return {"dados": data, "logs": logs}

    except requests.exceptions.ConnectTimeout:
        logs.append("❌ Timeout de conexão")
        return {"erro": "ConnectTimeout", "logs": logs}
    except requests.exceptions.ReadTimeout:
        logs.append("❌ Timeout de leitura")
        return {"erro": "ReadTimeout", "logs": logs}
    except Exception as e:
        logs.append(f"❌ Erro na requisição: {e}")
        return {"erro": str(e), "logs": logs}

def extrair_dados(dados):
    """Puxa apenas histórico e info complementares do JSON."""
    historico = dados.get("historico", "Histórico não encontrado")
    info      = dados.get("informacoes_complementares", "Informações complementares não encontradas")
    return historico.strip(), info.strip()

def gerar_template_email(historico, info):
    agora = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    h = historico.replace("\n", "<br>")
    i = info.replace("\n", "<br>")
    return f"""
    <div style="font-family:Arial,sans-serif; color:#333;">
      <h2 style="color:#004b87;">Histórico</h2>
      <p>{h}</p><hr>
      <h2 style="color:#004b87;">Informações Complementares</h2>
      <p>{i}</p><hr>
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
    resultado = consultar_proposicao(proposicao, numero, ano)
    if "erro" in resultado:
        assunto = f"[ERRO] ALEPE – {datetime.now():%d/%m/%Y}"
        enviar_email(assunto, "❌ Problema na execução", resultado["logs"])
        return {"status": "erro", "logs": resultado["logs"]}

    hist, info = extrair_dados(resultado["dados"])
    assunto = f"Atualização ALEPE – {numero}/{ano} – {datetime.now():%d/%m/%Y}"
    corpo   = gerar_template_email(hist, info)

    enviar_email(assunto, corpo, resultado["logs"])
    return {"status": "sucesso"}

if __name__ == "__main__":
    out = executar_robot("projetos", "3005", "2025")
    print(out)

