from fastapi import FastAPI, Request
from pydantic import BaseModel, Field
from services.extractor import extract_tasks_with_gemini
from typing import List
from models.task import TarefasPorPessoa
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

app = FastAPI()

# Configuração do rate limiting
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

class TextoEntrada(BaseModel):
    """Modelo de entrada para extração de tarefas a partir de texto de daily/reunião."""
    texto: str = Field(..., example="Lucas disse que ontem finalizou o componente de login, mas ainda precisa revisar a integração com o backend. ...")

@app.post(
    "/extract-tasks",
    response_model=List[TarefasPorPessoa],
    summary="Extrai tarefas de um texto de daily/reunião",
    response_description="Lista de tarefas agrupadas por responsável.",
    tags=["Extração"]
)
@limiter.limit("5/minute")
def extract(texto: TextoEntrada, request: Request):
    """
    Recebe um texto de daily/reunião e retorna um JSON estruturado com as tarefas feitas e a fazer, agrupadas por responsável.
    - **texto**: Texto da daily ou transcrição da reunião.
    - **Retorno**: Lista de objetos com responsável, tarefas feitas e tarefas a fazer (com prazo, data normalizada e descrição).
    """
    resultado = extract_tasks_with_gemini(texto.texto)
    return resultado