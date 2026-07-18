FROM python:3.11.13-slim

LABEL org.opencontainers.image.title="LeetCode Activity Tracker"
LABEL org.opencontainers.image.description="Production-oriented Python application that tracks LeetCode submissions and sends Telegram notifications."
LABEL org.opencontainers.image.licenses="MIT"

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt

COPY . ./

RUN useradd --create-home --shell /usr/sbin/nologin appuser && \
    chown -R appuser:appuser /app

USER appuser

CMD ["python", "main.py"]