FROM python:3.11-slim

WORKDIR /app

COPY api/requirements.txt .
RUN pip install --no-cache-dir -r api/requirements.txt

COPY api/main.py ./api/main.py
COPY data/eg_drugs.sqlite ./data/eg_drugs.sqlite

EXPOSE 8000

CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
