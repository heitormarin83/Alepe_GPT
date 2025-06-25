import os
import json
import requests
import yagmail
import xml.etree.ElementTree as ET
from datetime import datetime
from dotenv import load_dotenv

# Carrega variáveis de ambiente
load_dotenv()
EMAIL_USER         = os.getenv("EMAIL_USER")
EMAIL_APP_PASSWORD = os.getenv("EMAIL_APP_PASSWORD")
EMAIL_RECIPIENT    = os.getenv("EMAIL_RECIPIENT")

# Defaults (podem ser sobrescritos na chamada)
PROPOSICAO = os.getenv("PROPOSICAO", "projetos")
NUMERO     = os.getenv("NUMERO", "3005")
ANO        = os.getenv("ANO", "2025")

# Arquivos locais (persistência efêmera)
HISTORICO_FILE = "historico_anterior.txt"
INFO_FILE      = "info_complementar_anterior.txt"


def consultar_proposicao(proposicao, numero, ano):
    logs = ["🚀 Iniciando consulta via API da ALEPE"]
    url  = f"https://dadosabertos.alepe.pe.gov.br/api/v1/proposicoes/{proposicao}/?numero={numero}&ano={ano}"
    logs.append(f"🔗 GET {url}")

    try:
        resp = requests.get(
            url,
            headers={"Accept": "application/json, application/xml"},
            timeout=60
        )
        logs.append(f"📥 Status da resposta: {resp.status_code}")
        if resp.status_code != 200:
            logs.append(f"❌ API retornou status {resp.status_code}")
            return {"erro": f"Status {resp.status_code}", "logs": logs}

        text = resp.text or ""
        if not text.strip():
            logs.append("⚠️ Resposta vazia")
            return {"erro": "Resposta vazia", "logs": logs}

        ctype = resp.headers.get("Content-Type", "")
        return {"text": text, "content_type": ctype, "logs": logs}

    except Exception as e:
        logs.append(f"❌ Erro na requisição: {e}")
        return {"erro": str(e), "logs": logs}


def extrair_dados_xml(xml_text):
    try:
        root = ET.fromstring(xml_text)
    except ET.ParseError:
        return "", ""
    # Extrai eventos
    eventos = root.findall(".//historico/evento")
    historico = []
    for ev in eventos:
        data = ev.get("data", "")
        acao = ev.findtext("acao", "").strip()
        if data or acao:
            historico.append(f"{data} — {acao}")
    hist_text = "\n".join(historico) if historico else "Histórico não encontrado"
    # Extrai info complementar
    info = root.findtext(".//informacoesComplementares")
    info_text = info.strip() if info and info.strip() else "Informações complementares não encontradas"
    return hist_text, info_text


def carregar_anterior(path):
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return f.read().strip()
    return ""


def salvar_atual(path, texto):
    with open(path, "w", encoding="utf-8") as f:
        f.write(texto.strip())


def gerar_html(historico, info):
    ts = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    h = historico.replace("\n", "<br>")
    i = info.replace("\n", "<br>")
    return f"""
<div style="font-family:Arial,sans-serif;">
  <h2 style="color:#004b87;">Histórico</h2>
  <p>{h}</p>
  <hr>
  <h2 style="color:#004b87;">Informações Complementares</h2>
  <p>{i}</p>
  <hr>
  <p><small>Consulta realizada em {ts}</small></p>
</div>
"""


def enviar_email(assunto, html, logs):
    yag = yagmail.SMTP(EMAIL_USER, EMAIL_APP_PASSWORD)
    yag.send(
        to=EMAIL_RECIPIENT,
        subject=assunto,
        contents=[html, "<hr><pre>" + "\n".join(logs) + "</pre>"]
    )
    print("📧 E-mail enviado com sucesso!")


def executar_robot(proposicao, numero, ano):
    # 1) Consulta
    res = consultar_proposicao(proposicao, numero, ano)
    if "erro" in res:
        subj = f"[ERRO] ALEPE {numero}/{ano} - {datetime.now():%d/%m/%Y}"
        enviar_email(subj, f"<p>{res['erro']}</p>", res["logs"])
        return

    text = res["text"]
    ctype = res["content_type"].lower()
    logs  = res["logs"]

    # 2) Extrai histórico & info
    if "xml" in ctype or text.lstrip().startswith("<"):
        historico, info = extrair_dados_xml(text)
        logs.append("✅ XML parseado com sucesso")
    else:
        try:
            payload = json.loads(text)
            item    = payload.get("results", [{}])[0]
            historico = item.get("historico", "").strip() or "Histórico não encontrado"
            info      = item.get("informacoes_complementares", "").strip() or "Informações complementares não encontradas"
            logs.append("✅ JSON parseado com sucesso")
        except Exception as e:
            logs.append(f"❌ Falha ao tratar JSON: {e}")
            historico, info = "",""

    # 3) Carrega valores de ontem
    prev_h = carregar_anterior(HISTORICO_FILE)
    prev_i = carregar_anterior(INFO_FILE)

    # 4) Compara
    mudou = (historico != prev_h) or (info != prev_i)

    # 5) Salva para próxima vez
    salvar_atual(HISTORICO_FILE, historico)
    salvar_atual(INFO_FILE, info)

    # 6) Monta e envia e-mail
    emoji = "🟥" if mudou else "🟩"
    subj  = f"Status ALEPE - {numero}/{ano} - {datetime.now():%d/%m/%Y} {emoji}"
    html  = gerar_html(historico, info)
    enviar_email(subj, html, logs)


if __name__ == "__main__":
    executar_robot(PROPOSICAO, NUMERO, ANO)
