from enum import Enum
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

class ProvedorEnum(str, Enum):
    spacy = "spacy"
    gemini = "gemini"

class TextoRequest(BaseModel):
    texto: str
    provedor: ProvedorEnum = ProvedorEnum.spacy

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://tarefai-eta.vercel.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/extract-tasks")
def extract_tasks_endpoint(req: TextoRequest):
    try:
        if req.provedor == ProvedorEnum.spacy:
            from services.spacy_local import extract_tasks_with_spacy
            resultado = extract_tasks_with_spacy(req.texto)
        elif req.provedor == ProvedorEnum.gemini:
            from services.gemini_llm import extract_tasks_with_gemini
            resultado = extract_tasks_with_gemini(req.texto)
        else:
            raise HTTPException(status_code=400, detail="Provedor inválido.")
        # Se resultado for erro (dict com 'erro'), levanta HTTPException
        if isinstance(resultado, list) and resultado and isinstance(resultado[0], dict) and "erro" in resultado[0]:
            raise HTTPException(status_code=422, detail=resultado[0]["erro"])
        return resultado
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")