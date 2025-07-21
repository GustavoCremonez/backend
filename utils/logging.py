import logging
import sys

def setup_logging(level=logging.INFO):
    """
    Configura o logging padrão para o projeto.
    Args:
        level: Nível de logging (default: INFO)
    """
    logging.basicConfig(
        level=level,
        format='%(asctime)s %(levelname)s %(name)s %(message)s',
        handlers=[logging.StreamHandler(sys.stdout)]
    ) 