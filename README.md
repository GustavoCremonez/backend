# TarefAi Backend

Backend para extração automática de tarefas de textos de daily/reunião, utilizando LLM (Gemini) para análise semântica e retorno estruturado em JSON.

## ✨ Funcionalidades
- Recebe texto de daily/transcrição e retorna tarefas feitas e a fazer, separadas por responsável.
- Normaliza prazos em datas quando possível.
- Rate limiting, logging estruturado, modularização e segurança.
- Pronto para produção com Docker.

## 🚀 Tecnologias
- Python 3.12
- FastAPI
- Uvicorn
- Gemini API (Google)
- Pydantic
- SlowAPI (rate limiting)
- python-dotenv
- dateparser

## ⚙️ Requisitos
- Python 3.12+
- Conta e chave de API Gemini (https://aistudio.google.com/app/apikey)
- Docker (opcional, para deploy containerizado)

## 🛠️ Instalação e uso local
1. Clone o repositório e acesse a pasta:
   ```sh
   git clone <repo-url>
   cd backend
   ```
2. Crie e ative um ambiente virtual:
   ```sh
   python -m venv .venv
   source .venv/bin/activate  # Linux/Mac
   .venv\Scripts\activate    # Windows
   ```
3. Instale as dependências:
   ```sh
   pip install -r requirements.txt
   ```
4. Crie um arquivo `.env` na raiz com sua chave Gemini:
   ```env
   GEMINI_API_KEY=COLE_SUA_CHAVE_AQUI
   ```
5. Rode o servidor:
   ```sh
   uvicorn main:app --reload
   ```
6. Acesse a documentação interativa em [http://localhost:8000/docs](http://localhost:8000/docs)

## 🐳 Uso com Docker
1. Build da imagem:
   ```sh
   docker build -t tarefai-backend .
   ```
2. Rode o container (usando seu .env):
   ```sh
   docker run --env-file .env -p 8000:8000 tarefai-backend
   ```

## 🔑 Variáveis de ambiente
- `GEMINI_API_KEY`: **Obrigatória**. Chave da API Gemini (Google).

## 📋 Exemplo de request/response
### Request
```json
POST /extract-tasks
{
  "texto": "Lucas disse que ontem finalizou o componente de login, mas ainda precisa revisar a integração com o backend."
}
```
### Response
```json
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
```

## 🧪 Testes
Execute os testes automatizados com:
```sh
python -m unittest test_data/test_extractor.py
```

## 📚 Documentação
- Acesse `/docs` para Swagger/OpenAPI interativo.
- Modelos de entrada e saída documentados automaticamente.

## 👨‍💻 Contato
Dúvidas ou sugestões? Abra uma issue ou entre em contato! 