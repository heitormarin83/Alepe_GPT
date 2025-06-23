from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import yagmail
from datetime import datetime
import time
import os
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_APP_PASSWORD = os.getenv("EMAIL_APP_PASSWORD")
EMAIL_RECIPIENT = os.getenv("EMAIL_RECIPIENT")
DOCID = os.getenv("DOCID")
TIPOPROP = os.getenv("TIPOPROP")

def consultar_proposicao(docid, tipoprop):
    url = f"https://www.alepe.pe.gov.br/proposicao-texto-completo/?docid={docid}&tipoprop={tipoprop}"

    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--window-size=1920,1080")

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    try:
        driver.get(url)
        time.sleep(3)

        titulo = driver.find_element(By.CSS_SELECTOR, "h1.titulo").text
        ementa = driver.find_element(By.CSS_SELECTOR, "div.ementa").text

        try:
            historico = driver.find_element(By.XPATH, "//div[@id='historico']").text
        except:
            historico = "Não encontrado"

        try:
            info_complementar = driver.find_element(By.XPATH, "//div[@id='informacoesComplementares']").text
        except:
            info_complementar = "Não encontrado"

        dados = {
            "titulo": titulo,
            "ementa": ementa,
            "historico": historico,
            "info_complementar": info_complementar,
            "url": url
        }
        return dados

    except Exception as e:
        print(f"Erro: {e}")
        return None

    finally:
        driver.quit()

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
        print("E-mail enviado com sucesso!")
    except Exception as e:
        print(f"Erro ao enviar e-mail: {e}")

if __name__ == "__main__":
    dados = consultar_proposicao(DOCID, TIPOPROP)

    if dados:
        corpo_email = gerar_template_email(dados)
        assunto = f"Acompanhamento ALEPE - {dados['titulo']} - {datetime.now().strftime('%d/%m/%Y')}"
        enviar_email(assunto, corpo_email, EMAIL_RECIPIENT, EMAIL_USER, EMAIL_APP_PASSWORD)
    else:
        print("Erro na consulta da proposição.")
