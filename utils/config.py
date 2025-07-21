import os
from dotenv import load_dotenv
import logging

# Carrega as variáveis de ambiente de um arquivo .env se ele existir
load_dotenv()

def get_env_var(var_name: str, default: str = None, required: bool = False) -> str:
    """
    Busca uma variável de ambiente.
    Args:
        var_name: Nome da variável de ambiente.
        default: Valor padrão a ser retornado se a variável não for encontrada.
        required: Se True, lança um erro se a variável não for encontrada e não houver padrão.
    Returns:
        O valor da variável de ambiente.
    Raises:
        ValueError: Se a variável for obrigatória e não estiver definida.
    """
    value = os.getenv(var_name)
    if value is None:
        if required and default is None:
            logging.error(f"A variável de ambiente obrigatória '{var_name}' não foi definida.")
            raise ValueError(f"A variável de ambiente obrigatória '{var_name}' não foi definida.")
        return default
    return value 