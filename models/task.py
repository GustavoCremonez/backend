from pydantic import BaseModel
from typing import Optional

class TarefaAFazer(BaseModel):
    """Representa uma tarefa a fazer, com prazo, data normalizada e descrição opcional."""
    task: str
    prazo: Optional[str] = None
    data_prazo: Optional[str] = None
    descricao: Optional[str] = None