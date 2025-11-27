FROM python:3.9-slim

WORKDIR /app

# Instala dependências
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia os scripts
COPY server.py .
COPY load_balancer.py .
COPY client.py .

# Expõe as portas que podem ser usadas
EXPOSE 5000 5001 5002

# O comando será especificado no docker-compose
CMD ["python"]
