FROM python:3.13-slim

WORKDIR /app

COPY pyproject.toml README.md ./
COPY orchestrator ./orchestrator

RUN pip install --no-cache-dir .

EXPOSE 8000

CMD ["uvicorn", "orchestrator.main:app", "--host", "0.0.0.0", "--port", "8000"]
