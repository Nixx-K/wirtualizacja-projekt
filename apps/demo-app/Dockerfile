FROM python:3.11-slim

WORKDIR /app

# Kopiuj requirements i instaluj
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt && \
    pip list | grep prometheus  # Debugowanie - pokaże czy zainstalowało

# Kopiuj aplikację
COPY app.py .

# Port
EXPOSE 8000

# Healthcheck
HEALTHCHECK --interval=30s --timeout=3s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health').read()" || exit 1

# Użyj Gunicorn zamiast Flask dev server
CMD ["python", "-u", "app.py"]
