import os
from dotenv import load_dotenv

load_dotenv()

def get_env_var(key: str, default: str = None, required: bool = False) -> str:
    value = os.getenv(key, default)
    if required and not value:
        raise RuntimeError(f"Variável de ambiente obrigatória não definida: {key}")
    return value 