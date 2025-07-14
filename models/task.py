from pydantic import BaseModel

class TarefaExtraida(BaseModel):
    responsavel: str
    tarefa: str
    prazo: str | None