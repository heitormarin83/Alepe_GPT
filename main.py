import requests
from datetime import datetime
import yagmail
import os
import json
from dotenv import load_dotenv

# Carrega variáveis de ambiente
load_dotenv()

EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_APP_PASSWORD = os.getenv("EMAIL_APP_PASSWORD")
EMAIL_RECIPIENT = os.getenv("EMAIL_RECIPIENT")

# Arquivo para armazenar o histórico anterior
ARQUIVO_HISTORICO = "dados_anteriores.json"


def consultar_proposicao(proposicao, numero, ano):
    logs = []
    logs.append("🚀 Iniciando captura via API da ALEPE")

    url = f"https://dadosabertos.alepe.pe.gov.br/api/v1/proposicoes/{proposicao}/?numero={numero}&ano={ano}"
    logs.append(f"🔗 Acessando API: {url}")

    try:
        response = requests.get(url, timeout=60)
        logs.append(f"📥 Status da resposta: {response.status_code}")

        if response.status_code != 200:
            logs.append(f"❌ Erro na API: {response.status_code} - {response.text}")
            return {"erro": f"API retornou status {response.status_code}", "logs": logs}

        if not response.text.strip():
            logs.append("⚠️ Resposta vazia da API.")
            return {"erro": "Resposta vazia", "logs": logs}

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


def extrair_dados_interesse(dados):
    historico = dados.get("historico", "Não encontrado")
    informacoes_complementares = dados.get("informacoes_complementares", "Não encontrado")
    return historico.strip(), informacoes_complementares.strip()


def carregar_dados_anteriores():
    if os.path.exists(ARQUIVO_HISTORICO):
        with open(ARQUIVO_HISTORICO, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def salvar_dados_atuais(historico, info_complementar):
    dados = {
        "historico": historico,
        "informacoes_complementares": info_complementar
    }
    with open(ARQUIVO_HISTORICO, "w", encoding="utf-8") as f:
        json.dump(dados, f, ensure_ascii=False, indent=4)


def houve_alteracao(historico_atual, info_atual, historico_ant, info_ant):
    return historico_atual != historico_ant or info_atual != info_ant


def gerar_corpo_email(historico, info_complementar):
    return f"""
    <div style="font-family:Arial; color:#333;">
        <h2 style="color:#004b87;">Acompanhamento da Proposição</h2>
        <h3 style="color:#004b87;">Histórico</h3>
        <p>{historico.replace("\n", "<br>")}</p>
        <hr>
        <h3 style="color:#004b87;">Informações Complementares</h3>
        <p>{info_complementar.replace("\n", "<br>")}</p>
    </div>
    """


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


def executar_robot(proposicao, numero, ano):
    print("🚀 Iniciando execução do Alepe_GPT com API")
    resultado = consultar_proposicao(proposicao, numero, ano)

    if 'erro' in resultado:
        assunto = f"[ERRO] Alepe GPT - {datetime.now().strftime('%d/%m/%Y')}"
        enviar_email(assunto, "❌ Erro na execução", resultado['logs'])
        return {"status": "erro", "logs": resultado['logs']}

    dados = resultado['dados']
    historico_atual, info_atual = extrair_dados_interesse(dados)

    dados_anteriores = carregar_dados_anteriores()
    historico_ant = dados_anteriores.get("historico", "")
    info_ant = dados_anteriores.get("informacoes_complementares", "")

    alteracao = houve_alteracao(historico_atual, info_atual, historico_ant, info_ant)

    status_cor = "🟥" if alteracao else "🟩"
    status_texto = "Movimentação Detectada" if alteracao else "Sem Movimentação"

    assunto = f"Status ALEPE - {numero}/{ano} - {datetime.now().strftime('%d/%m/%Y')} {status_cor} {status_texto}"

    corpo = gerar_corpo_email(historico_atual, info_atual)

    enviar_email(assunto, corpo, resultado['logs'])

    salvar_dados_atuais(historico_atual, info_atual)

    return {"status": "sucesso", "alteracao": alteracao, "logs": resultado['logs']}


if __name__ == "__main__":
    resultado = executar_robot("projetos", "3005", "2025")
    print(resultado)


if __name__ == "__main__":
    resultado = executar_robot()
    print(resultado)
