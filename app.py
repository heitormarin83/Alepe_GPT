from fastapi import FastAPI, Query
from main import executar_robot_parametrizado

app = FastAPI()


@app.get("/")
def read_root():
    return {"status": "OK", "message": "Alepe GPT API rodando."}


@app.get("/run")
def run_robot(
    docid: str = Query(..., description="Código da proposição"),
    tipoprop: str = Query(..., description="Tipo da proposição, ex: p")
):
    resultado = executar_robot_parametrizado(docid, tipoprop)
    return resultado
