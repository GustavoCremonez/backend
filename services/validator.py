import dateparser
from datetime import datetime
from typing import List, Dict, Any

def normalize_date(expr: str, base_date: datetime = None) -> str:
    if not expr:
        return ""
    if base_date is None:
        base_date = datetime.now()
    dt = dateparser.parse(expr, settings={"RELATIVE_BASE": base_date, "PREFER_DATES_FROM": "future", "DATE_ORDER": "DMY"})
    if dt:
        return dt.strftime("%Y-%m-%d")
    return ""

def postprocess_tasks(data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Normaliza datas das tarefas a fazer e pode incluir outras validações/pós-processamentos.
    """
    for pessoa in data:
        if "a_fazer" in pessoa:
            for tarefa in pessoa["a_fazer"]:
                prazo_expr = tarefa.get("prazo", "")
                tarefa["data_prazo"] = normalize_date(prazo_expr)
    return data 