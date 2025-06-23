from fastapi import FastAPI, Query
from main import executar_robot

app = FastAPI()


@app.get("/")
def read_root():
    return {"status": "OK", "message": "Alepe GPT API rodando."}


@app.get("/run")
def run_robot(
    docid: str = Query(None, description="Código da proposição (opcional, usa DOCID do .env se não enviar)"),
    tipoprop: str = Query(None, description="Tipo da proposição, ex: p (opcional, usa TIPOPROP do .env se não enviar)")
):
    resultado = executar_robot(docid=docid, tipoprop=tipoprop)
    return resultado

