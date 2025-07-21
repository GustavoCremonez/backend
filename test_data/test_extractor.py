import unittest
from unittest.mock import patch, MagicMock
from services.spacy_local import extract_tasks_with_spacy
from services.gemini_llm import extract_tasks_with_gemini
from services.validator import normalize_date, postprocess_tasks
from models.task import TarefaAFazer
from utils.config import get_env_var
from fastapi.testclient import TestClient
import main
from datetime import datetime

class TestExtractor(unittest.TestCase):
    def test_extract_tasks_with_spacy_simple(self):
        texto = "Lucas: Ontem finalizei o componente de login, mas ainda preciso revisar a integração com o backend."
        resultado = extract_tasks_with_spacy(texto)
        print("Resultado spacy simple:", resultado)
        nomes = [p['responsavel'] for p in resultado]
        self.assertTrue("Lucas" in nomes or "Desconhecido" in nomes)
        lucas = next((p for p in resultado if p['responsavel'] == 'Lucas'), None)
        if lucas:
            self.assertTrue(len(lucas['feitas']) > 0 or len(lucas['a_fazer']) > 0)
        else:
            desconhecido = next((p for p in resultado if p['responsavel'] == 'Desconhecido'), None)
            self.assertIsNotNone(desconhecido)
            self.assertTrue(len(desconhecido['feitas']) > 0 or len(desconhecido['a_fazer']) > 0)

    def test_extract_tasks_with_spacy_complex(self):
        texto = """João: Ontem finalizei o ajuste no endpoint de faturamento e fiz o merge na develop. Hoje vou revisar o PR da Alê e começar a refatorar o serviço de autenticação."""
        resultado = extract_tasks_with_spacy(texto)
        print("Resultado spacy complex:", resultado)
        joao = next((p for p in resultado if p['responsavel'] == 'João'), None)
        self.assertIsNotNone(joao)
        self.assertGreaterEqual(len(joao['feitas']), 1)
        self.assertGreaterEqual(len(joao['a_fazer']), 1)

    @patch('services.gemini_llm.requests.post')
    def test_extract_tasks_with_gemini_success(self, mock_post):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "candidates": [{
                "content": {
                    "parts": [{
                        "text": """
                        [
                            {
                                "responsavel": "Lucas",
                                "feitas": ["Finalizou o componente de login"],
                                "a_fazer": [
                                    {
                                        "task": "Revisar a integração com o backend",
                                        "prazo": "",
                                        "data_prazo": "",
                                        "descricao": ""
                                    }
                                ]
                            }
                        ]
                        """
                    }]
                }
            }]
        }
        mock_post.return_value = mock_response
        texto = "Lucas disse que ontem finalizou o componente de login, mas ainda precisa revisar a integração com o backend."
        resultado = extract_tasks_with_gemini(texto)
        self.assertEqual(resultado[0]['responsavel'], "Lucas")
        self.assertIn("Finalizou o componente de login", resultado[0]['feitas'])

    @patch('services.gemini_llm.requests.post')
    def test_extract_tasks_with_gemini_error(self, mock_post):
        mock_post.side_effect = Exception("Erro de comunicação")
        texto = "Texto inválido ou erro na IA."
        resultado = extract_tasks_with_gemini(texto)
        self.assertIn("erro", resultado[0])

    def test_normalize_date(self):
        ano_atual = str(datetime.now().year)
        self.assertEqual(normalize_date("amanhã", base_date=None)[:4], ano_atual)
        self.assertEqual(normalize_date("", base_date=None), "")

    def test_postprocess_tasks(self):
        data = [{"responsavel": "Lucas", "a_fazer": [{"prazo": "amanhã"}]}]
        processed = postprocess_tasks(data)
        self.assertIn("data_prazo", processed[0]["a_fazer"][0])

    def test_tarefa_a_fazer_model(self):
        tarefa = TarefaAFazer(task="Testar", prazo="amanhã", data_prazo="2025-07-22", descricao="desc")
        self.assertEqual(tarefa.task, "Testar")
        self.assertEqual(tarefa.prazo, "amanhã")
        self.assertEqual(tarefa.data_prazo, "2025-07-22")
        self.assertEqual(tarefa.descricao, "desc")

    def test_get_env_var(self):
        import os
        os.environ["TEST_ENV_VAR"] = "valor"
        self.assertEqual(get_env_var("TEST_ENV_VAR"), "valor")
        self.assertEqual(get_env_var("INEXISTENTE", default="padrao"), "padrao")
        with self.assertRaises(ValueError):
            get_env_var("OBRIGATORIA", required=True)

    def test_fastapi_endpoint_spacy(self):
        client = TestClient(main.app)
        response = client.post("/extract-tasks", json={"texto": "Lucas: Ontem finalizei o componente de login.", "provedor": "spacy"})
        print("FastAPI spacy response:", response.json())
        self.assertEqual(response.status_code, 200)
        nomes = [p["responsavel"] for p in response.json()]
        self.assertTrue("Lucas" in nomes or "Desconhecido" in nomes)

    @patch('services.gemini_llm.requests.post')
    def test_fastapi_endpoint_gemini(self, mock_post):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "candidates": [{
                "content": {
                    "parts": [{
                        "text": """
                        [
                            {
                                "responsavel": "Lucas",
                                "feitas": ["Finalizou o componente de login"],
                                "a_fazer": [
                                    {
                                        "task": "Revisar a integração com o backend",
                                        "prazo": "",
                                        "data_prazo": "",
                                        "descricao": ""
                                    }
                                ]
                            }
                        ]
                        """
                    }]
                }
            }]
        }
        mock_post.return_value = mock_response
        client = TestClient(main.app)
        response = client.post("/extract-tasks", json={"texto": "Lucas: Ontem finalizei o componente de login.", "provedor": "gemini"})
        print("FastAPI gemini response:", response.json())
        self.assertEqual(response.status_code, 200)
        nomes = [p["responsavel"] for p in response.json()]
        self.assertTrue("Lucas" in nomes or "Desconhecido" in nomes)

if __name__ == "__main__":
    unittest.main() 