# Usa una versione ufficiale di Python come base
FROM python:3.10-slim

# Imposta la directory di lavoro
WORKDIR /app

# Copia i requisiti del progetto
COPY requirements.txt requirements.txt

# Installa le dipendenze
RUN pip install --no-cache-dir -r requirements.txt

# Copia il codice del progetto
COPY . .

# Imposta il comando di avvio per l'app
CMD ["python", "endpoint.py"]
