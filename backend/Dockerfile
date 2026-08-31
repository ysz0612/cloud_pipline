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
RUN mkdir -p /app/app/auth
RUN mkdir -p /app/app/users

COPY app/__init__.py ./app/__init__.py
COPY app/main.py ./app/main.py
COPY app/config.py ./app/config.py
COPY app/database.py ./app/database.py
COPY app/redis_client.py ./app/redis_client.py

COPY app/imageRag/__init__.py ./app/imageRag/__init__.py
COPY app/imageRag/schema.py ./app/imageRag/schema.py
COPY app/imageRag/service.py ./app/imageRag/service.py
COPY app/imageRag/web.py ./app/imageRag/web.py

COPY app/storage/__init__.py ./app/storage/__init__.py
COPY app/storage/s3.py ./app/storage/s3.py

COPY app/users/__init__.py ./app/users/__init__.py
COPY app/users/model.py ./app/users/model.py

COPY app/auth/__init__.py ./app/auth/__init__.py
COPY app/auth/schema.py ./app/auth/schema.py
COPY app/auth/security.py ./app/auth/security.py
COPY app/auth/service.py ./app/auth/service.py
COPY app/auth/dependencies.py ./app/auth/dependencies.py
COPY app/auth/web.py ./app/auth/web.py

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]