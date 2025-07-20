# Use imagem oficial do Python
FROM python:3.12-slim

# Diretório de trabalho
WORKDIR /app

# Copie os arquivos de requirements e instale dependências
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copie o restante do código
COPY . .

# Variável de ambiente para produção
ENV PYTHONUNBUFFERED=1

# Exponha a porta padrão do FastAPI/Uvicorn
EXPOSE 8000

# Comando para rodar o servidor
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"] 