FROM python:3.12-slim
WORKDIR /app
RUN apt-get update && apt-get install -y libpq-dev gcc
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["bash", "-lc", "cd src && uvicorn main:app --reload --host 0.0.0.0 --port 8000"]
