from playwright.sync_api import sync_playwright
import yagmail
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_APP_PASSWORD = os.getenv("EMAIL_APP_PASSWORD")
EMAIL_RECIPIENT = os.getenv("EMAIL_RECIPIENT")
DOCID = os.getenv("DOCID")
TIPOPROP = os.getenv("TIPOPROP")


def consultar_proposicao(docid, tipoprop):
    url = f"https://www.alepe.pe.gov.br/proposicao-texto-completo/?docid={docid}&tipoprop={tipoprop}"

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        page.goto(url, timeout=60000)

        titulo = page.locator("h1.titulo").inner_text()
        ementa = page.locator("div.ementa").inner_text()

        try:
            historico = page.locator("#historico").inner_text()
        except:
            historico = "Não encontrado"

        try:
            info_complementar = page.locator("#informacoesComplementares").inner_text()
        except:
            info_complementar = "Não encontrado"

        browser.close()

        return {
            "titulo": titulo,
            "ementa": ementa,
            "historico": historico,
            "info_complementar": info_complementar,
            "url": url
        }


def gerar_template_email(dados):
    agora = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
    html = f"""
    <div style="font-family:Arial; color:#333;">
        <h2 style="color:#004b87;">{dados['titulo']}</h2>
        <p><strong>Ementa:</strong><br>{dados['ementa']}</p>
        <hr>
        <h3 style="color:#004b87;">Histórico</h3>
        <p>{dados['historico'].replace("\n", "<br>")}</p>
        <hr>
        <h3 style="color:#004b87;">Informações Complementares</h3>
        <p>{dados['info_complementar'].replace("\n", "<br>")}</p>
        <hr>
        <p>
            <small>Consulta realizada em {agora} | 
            <a href="{dados['url']}" target="_blank">Acessar Proposição</a></small>
        </p>
    </div>
    """
    return html


def enviar_email(assunto, corpo_html, destinatario, remetente, senha_app):
    try:
        yag = yagmail.SMTP(remetente, senha_app)
        yag.send(
            to=destinatario,
            subject=assunto,
            contents=corpo_html
        )
        print("✅ E-mail enviado com sucesso!")
    except Exception as e:
        print(f"❌ Erro ao enviar e-mail: {e}")


if __name__ == "__main__":
    dados = consultar_proposicao(DOCID, TIPOPROP)

    if dados:
        corpo_email = gerar_template_email(dados)
        assunto = f"Acompanhamento ALEPE - {dados['titulo']} - {datetime.now().strftime('%d/%m/%Y')}"
        enviar_email(assunto, corpo_email, EMAIL_RECIPIENT, EMAIL_USER, EMAIL_APP_PASSWORD)
    else:
        print("Erro na consulta da proposição.")
