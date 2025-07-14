from fastapi import FastAPI, Request
from pydantic import BaseModel
from services.extractor import extract_tasks
from typing import List

app = FastAPI()

class TextoEntrada(BaseModel):
    texto: str

@app.post("/extract-tasks")
def extract(texto: TextoEntrada):
    resultado = extract_tasks(texto.texto)
    return resultado