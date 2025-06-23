from playwright.sync_api import sync_playwright
import yagmail
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_APP_PASSWORD = os.getenv("EMAIL_APP_PASSWORD")
EMAIL_RECIPIENT = os.getenv("EMAIL_RECIPIENT")


def consultar_proposicao(docid, tipoprop):
    url = f"https://www.alepe.pe.gov.br/proposicao-texto-completo/?docid={docid}&tipoprop={tipoprop}"
    print(f"🔗 Acessando: {url}")

    try:
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

    except Exception as e:
        print(f"❌ Erro na captura: {e}")
        return None


def gerar_template_email(dados):
    agora = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
    html = f"""
    <div style="font-family:Arial; color:#333;">
        <h2 style="color:#004b87;">{dados['titulo']}</h2>
        <p><strong>Ementa:</strong><br>{dados['ementa']}</p>
        <hr>
        <h3 style="color:#004b87;">Histórico</h3>
       historico_formatado = dados['historico'].replace("\n", "<br>")
html = f"""
    <p>{historico_formatado}</p>
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


def enviar_email(assunto, corpo_html):
    try:
        yag = yagmail.SMTP(EMAIL_USER, EMAIL_APP_PASSWORD)
        yag.send(
            to=EMAIL_RECIPIENT,
            subject=assunto,
            contents=corpo_html
        )
        print("✅ E-mail enviado com sucesso!")
    except Exception as e:
        print(f"❌ Erro ao enviar e-mail: {e}")


def executar_robot_parametrizado(docid, tipoprop):
    dados = consultar_proposicao(docid, tipoprop)

    if dados:
        corpo_email = gerar_template_email(dados)
        assunto = f"Acompanhamento ALEPE - {dados['titulo']} - {datetime.now().strftime('%d/%m/%Y')}"
        enviar_email(assunto, corpo_email)
        return {
            "status": "sucesso",
            "dados": dados
        }
    else:
        return {
            "status": "erro",
            "mensagem": "Não foi possível capturar os dados da proposição."
        }


if __name__ == "__main__":
    resultado = executar_robot()
    print("🔁 Mantendo o container aberto para debug...")
    time.sleep(300)  # 5 minutos
