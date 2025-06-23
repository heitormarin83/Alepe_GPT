from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError
import yagmail
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

# Variáveis de ambiente
EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_APP_PASSWORD = os.getenv("EMAIL_APP_PASSWORD")
EMAIL_RECIPIENT = os.getenv("EMAIL_RECIPIENT")
DOCID = os.getenv("DOCID")
TIPOPROP = os.getenv("TIPOPROP")


def consultar_proposicao(docid, tipoprop):
    logs = []
    logs.append("🚀 Iniciando captura da proposição")
    url = f"https://www.alepe.pe.gov.br/proposicao-texto-completo/?docid={docid}&tipoprop={tipoprop}"
    logs.append(f"🔗 Acessando: {url}")

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()

            page.goto(url, timeout=120000)  # Aumentei o timeout para carregar

            def captura_seletor(seletor, descricao):
                try:
                    page.wait_for_selector(seletor, timeout=30000)
                    valor = page.locator(seletor).inner_text()
                    return valor
                except PlaywrightTimeoutError:
                    logs.append(f"⚠️ {descricao} não encontrado.")
                    return f"{descricao} não encontrado"
                except Exception as e:
                    logs.append(f"❌ Erro ao capturar {descricao}: {e}")
                    return f"{descricao} não encontrado"

            titulo = captura_seletor("h1.titulo", "Título")
            ementa = captura_seletor("div.ementa", "Ementa")
            historico = captura_seletor("#historico", "Histórico")
            info_complementar = captura_seletor("#informacoesComplementares", "Informações Complementares")

            browser.close()

            logs.append("✅ Dados capturados com sucesso")
            return {
                "titulo": titulo,
                "ementa": ementa,
                "historico": historico,
                "info_complementar": info_complementar,
                "url": url,
                "log": logs
            }

    except Exception as e:
        logs.append(f"❌ Erro na captura: {e}")
        return {"erro": str(e), "log": logs}


def gerar_template_email(dados):
    agora = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
    historico = dados['historico'].replace("\n", "<br>")
    info_complementar = dados['info_complementar'].replace("\n", "<br>")

    html = f"""
    <div style="font-family:Arial; color:#333;">
        <h2 style="color:#004b87;">{dados['titulo']}</h2>
        <p><strong>Ementa:</strong><br>{dados['ementa']}</p>
        <hr>
        <h3 style="color:#004b87;">Histórico</h3>
        <p>{historico}</p>
        <hr>
        <h3 style="color:#004b87;">Informações Complementares</h3>
        <p>{info_complementar}</p>
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


def executar_robot(docid=None, tipoprop=None):
    print("🚀 Iniciando execução do Alepe_GPT")
    docid = docid or DOCID
    tipoprop = tipoprop or TIPOPROP

    dados = consultar_proposicao(docid, tipoprop)

    if 'erro' in dados:
        assunto = f"[ERRO] Alepe GPT - {datetime.now().strftime('%d/%m/%Y')}"
        enviar_email(assunto, "Erro na execução", dados.get('log', []))
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
