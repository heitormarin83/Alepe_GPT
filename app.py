from fastapi import FastAPI
from main import executar_robot

app = FastAPI()

@app.get("/")
def read_root():
    return {"status": "OK", "message": "Alepe GPT API rodando."}

@app.get("/run")
def run_robot():
    resultado = executar_robot()
    return resultado
