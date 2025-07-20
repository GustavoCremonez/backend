from pydantic import BaseModel
from typing import List, Optional

class TarefaAFazer(BaseModel):
    """Representa uma tarefa a fazer, com prazo, data normalizada e descrição opcional."""
    task: str
    prazo: Optional[str] = None
    data_prazo: Optional[str] = None
    descricao: Optional[str] = None

class TarefasPorPessoa(BaseModel):
    """Modelo de resposta agrupando tarefas feitas e a fazer por responsável."""
    responsavel: str
    feitas: List[str]
    a_fazer: List[TarefaAFazer]