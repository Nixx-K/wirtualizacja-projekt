FROM python:3.11-slim

WORKDIR /app

#copy requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py .

EXPOSE 8000

#uruchamianie
CMD ["python", "app.py"]
