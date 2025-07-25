import os
import requests
from typing import List, Dict, Any
import json
import re
from dotenv import load_dotenv
import logging
from services.validator import postprocess_tasks
from utils.config import get_env_var
from utils.logging import setup_logging

setup_logging()

logger = logging.getLogger(__name__)

PROMPT_TEMPLATE = """
Analise o texto abaixo, identifique para cada pessoa:
- O que foi feito
- O que vai ser feito

Para cada tarefa a fazer, retorne um objeto com:
- task: nome da tarefa
- prazo: expressão do prazo (ex: amanhã, sexta-feira, fim do dia)
- data_prazo: data no formato AAAA-MM-DD se possível identificar, senão deixe vazio
- descricao: pequena descrição adicional se houver

Retorne um JSON no formato:
[
  {{
    "responsavel": "Nome",
    "feitas": ["tarefa1", ...],
    "a_fazer": [
      {{
        "task": "nome da tarefa",
        "prazo": "expressão do prazo",
        "data_prazo": "AAAA-MM-DD",
        "descricao": "descrição adicional"
      }}
    ]
  }}
]

Texto: {texto}
"""

def extract_tasks_with_gemini(texto: str) -> List[Dict[str, Any]]:
    GEMINI_API_KEY = get_env_var("GEMINI_API_KEY", required=True)
    GEMINI_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={GEMINI_API_KEY}"
    prompt = PROMPT_TEMPLATE.format(texto=texto)
    payload = {
        "contents": [{"parts": [{"text": prompt}]}]
    }
    logger.info("Enviando requisição para Gemini API.")
    try:
        response = requests.post(GEMINI_URL, json=payload, timeout=30)
        response.raise_for_status()
        logger.info("Resposta recebida da Gemini API com status %s", response.status_code)
        
        response_data = response.json()
        
        if "candidates" not in response_data or not response_data["candidates"]:
            logger.error("Resposta da Gemini não contém 'candidates'. Resposta: %s", response_data)
            return [{"erro": "Formato de resposta inesperado da IA."}]

        result_text = response_data["candidates"][0]["content"]["parts"][0]["text"]
        
        clean_text = re.sub(r'```json\n?|```', '', result_text.strip())

        try:
            data = json.loads(clean_text)
            return postprocess_tasks(data)
        except json.JSONDecodeError as e:
            logger.error("Erro ao decodificar o JSON da Gemini: %s. Resposta recebida: %s", e, clean_text)
            return [{"erro": "Erro ao processar a resposta da IA. Formato JSON inválido."}]
            
    except requests.RequestException as e:
        logger.error("Erro de comunicação com a Gemini API: %s", e)
        return [{"erro": "Erro de comunicação com a IA. Tente novamente mais tarde."}]
    except Exception as e:
        logger.critical("Erro inesperado: %s", e)
        return [{"erro": "Erro inesperado. Tente novamente mais tarde."}]