from fastapi import FastAPI, Query
from main import executar_robot

app = FastAPI()


@app.get("/")
def read_root():
    return {"status": "OK", "message": "Alepe GPT API rodando."}


@app.get("/run")
def run_robot(
    proposicao: str = Query(None, description="Tipo da proposição, ex: projetos"),
    numero: str = Query(None, description="Número da proposição"),
    ano: str = Query(None, description="Ano da proposição")
):
    resultado = executar_robot(proposicao=proposicao, numero=numero, ano=ano)
    return resultado
