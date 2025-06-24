from fastapi import FastAPI, Query
from main import executar_robot

app = FastAPI()

@app.get("/")
def read_root():
    return {"status": "OK", "message": "Alepe GPT API rodando."}


@app.get("/run")
def run_robot(
    proposicao: str = Query(..., description="Tipo da proposição, exemplo: projetos"),
    numero: str = Query(..., description="Número da proposição"),
    ano: str = Query(..., description="Ano da proposição")
):
    resultado = executar_robot(proposicao, numero, ano)
    return resultado
