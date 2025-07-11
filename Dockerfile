# Usar imagen base compatible con Rasa 3.6.0
FROM python:3.10-slim

# Evitar interacciones durante la instalación
ENV DEBIAN_FRONTEND=noninteractive

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Actualizar pip
RUN python -m pip install --upgrade pip

# Crear directorio de trabajo
RUN mkdir -p /root/server
WORKDIR /root/server

# Copiar requirements.txt primero para aprovechar la cache de Docker
COPY server/requirements.txt .

# Instalar dependencias de Python
RUN pip install --no-cache-dir -r requirements.txt

# Instalar spaCy con modelo en español y descargar datos NLTK y modelo transformers
RUN python -m spacy download es_core_news_md && \
    python -m spacy download es_dep_news_trf && \
    python -c "import nltk; nltk.download('stopwords'); nltk.download('punkt')"

# Copiar el resto del código
COPY server/ .

# Crear directorios necesarios
RUN mkdir -p training_data/intents core/config models

# Exponer puerto
EXPOSE 5001

# Comando por defecto
CMD ["python", "app.py"]
