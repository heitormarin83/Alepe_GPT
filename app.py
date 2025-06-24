from fastapi import FastAPI
from main import executar_robot

app = FastAPI()


@app.get("/")
def read_root():
    return {"status": "ok", "message": "Alepe GPT API funcionando"}


@app.get("/run")
def run_robot():
    resultado = executar_robot("projetos", "3005", "2025")
    return resultado
