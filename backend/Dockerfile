FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PIP_NO_CACHE_DIR=1

WORKDIR /app

COPY requirements.txt .

RUN pip install --upgrade pip \
    && pip install -r requirements.txt

RUN mkdir -p /app/app/imageRag
RUN mkdir -p /app/app/storage

COPY app/__init__.py ./app/__init__.py
COPY app/main.py ./app/main.py
COPY app/config.py ./app/config.py

COPY app/imageRag/__init__.py ./app/imageRag/__init__.py
COPY app/imageRag/schema.py ./app/imageRag/schema.py
COPY app/imageRag/service.py ./app/imageRag/service.py
COPY app/imageRag/web.py ./app/imageRag/web.py

COPY app/storage/__init__.py ./app/storage/__init__.py
COPY app/storage/s3.py ./app/storage/s3.py

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]