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
    print("🚀 Iniciando captura da proposição")
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

            print("✅ Dados capturados com sucesso")
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
    print("📝 Gerando template do e-mail")
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


def enviar_email(assunto, corpo_html):
    print("📧 Preparando envio de e-mail")
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


def validar_variaveis():
    print("🔍 Verificando variáveis de ambiente")
    variaveis = [EMAIL_USER, EMAIL_APP_PASSWORD, EMAIL_RECIPIENT, DOCID, TIPOPROP]
    nomes = ["EMAIL_USER", "EMAIL_APP_PASSWORD", "EMAIL_RECIPIENT", "DOCID", "TIPOPROP"]

    for valor, nome in zip(variaveis, nomes):
        if not valor:
            print(f"⚠️ Variável de ambiente {nome} não definida!")
            return False
    print("✔️ Todas as variáveis estão definidas.")
    return True


if __name__ == "__main__":
    print("🚀 Iniciando execução do Alepe_GPT")

    if not validar_variaveis():
        print("❌ Encerrando execução. Variáveis faltando.")
        exit(1)

    dados = consultar_proposicao(DOCID, TIPOPROP)

    if dados:
        print("🟩 Dados capturados:", dados)
        corpo_email = gerar_template_email(dados)
        assunto = f"Acompanhamento ALEPE - {dados['titulo']} - {datetime.now().strftime('%d/%m/%Y')}"
        enviar_email(assunto, corpo_email)
    else:
        print("❌ Não foi possível capturar os dados da proposição.")
