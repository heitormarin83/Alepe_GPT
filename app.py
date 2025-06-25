import os
from fastapi import FastAPI, Query
from dotenv import load_dotenv
from main import executar_robot

# Carrega .env e defaults
load_dotenv()
DEFAULT_PROP   = os.getenv("PROPOSICAO", "projetos")
DEFAULT_NUM    = os.getenv("NUMERO",     "3005")
DEFAULT_ANO    = os.getenv("ANO",        "2025")

app = FastAPI()


@app.get("/")
def read_root():
    return {
        "status": "OK",
        "message": "Alepe GPT API rodando."
    }


@app.get("/run")
def run_robot(
    proposicao: str = Query(
        DEFAULT_PROP,
        description="Tipo da proposição (ex: projetos, indicacoes etc)"
    ),
    numero: str = Query(
        DEFAULT_NUM,
        description="Número da proposição"
    ),
    ano: str = Query(
        DEFAULT_ANO,
        description="Ano da proposição"
    )
):
    """
    Dispara a captura da proposição.
    Se não passar parâmetros, usa os defaults do .env.
    """
    executar_robot(proposicao, numero, ano)
    return {
        "status": "enviado",
        "proposicao": proposicao,
        "numero": numero,
        "ano": ano
    }
