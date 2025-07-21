from enum import Enum
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

class ProvedorEnum(str, Enum):
    spacy = "spacy"
    gemini = "gemini"

class TextoRequest(BaseModel):
    texto: str
    provedor: ProvedorEnum = ProvedorEnum.spacy

app = FastAPI()

@app.post("/extract-tasks")
def extract_tasks_endpoint(req: TextoRequest):
    if req.provedor == ProvedorEnum.spacy:
        from services.spacy_local import extract_tasks_with_spacy
        return extract_tasks_with_spacy(req.texto)
    elif req.provedor == ProvedorEnum.gemini:
        from services.gemini_llm import extract_tasks_with_gemini
        return extract_tasks_with_gemini(req.texto)