FROM python:3.12-slim as builder

WORKDIR /app
COPY ./api/predict/requirements.txt .

RUN pip install --no-cache-dir --user -r requirements.txt && \
    find /root/.local -name '*.pyc' -delete && \
    find /root/.local -name '__pycache__' -delete

FROM python:3.12-slim

WORKDIR /app

COPY --from=builder /root/.local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY ./api/predict /app
COPY ./ml/models /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app

RUN adduser --disabled-password --gecos "" appuser
USER appuser

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1
