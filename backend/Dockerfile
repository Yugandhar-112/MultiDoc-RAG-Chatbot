FROM python:3.11-slim

WORKDIR /app

# System deps needed to build some Python packages (e.g. tokenizers)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Pre-download the embedding model into the image so the first request
# after deploy doesn't pay a slow download + cold-start penalty.

COPY app ./app

RUN mkdir -p /app/data/chroma_db

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
