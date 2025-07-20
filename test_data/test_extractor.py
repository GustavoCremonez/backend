import unittest
from unittest.mock import patch, MagicMock
from services.extractor import extract_tasks_with_gemini

class TestExtractor(unittest.TestCase):
    @patch('services.extractor.requests.post')
    def test_extract_tasks_success(self, mock_post):
        # Simula resposta da Gemini
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

    @patch('services.extractor.requests.post')
    def test_extract_tasks_error(self, mock_post):
        # Simula erro de comunicação
        mock_post.side_effect = Exception("Erro de comunicação")
        texto = "Texto inválido ou erro na IA."
        resultado = extract_tasks_with_gemini(texto)
        self.assertIn("erro", resultado[0])

if __name__ == "__main__":
    unittest.main() 