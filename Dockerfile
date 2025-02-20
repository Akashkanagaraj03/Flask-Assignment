FROM python:3.12-slim

RUN pip install poetry==2.1.1

WORKDIR /app

COPY pyproject.toml poetry.lock ./
COPY src ./src

#RUN apt-get update && apt-get install -y \         #enable in pg_config is needed
#    curl \
#    build-essential \
#    libpq-dev \
#    gcc \
#    && rm -rf /var/lib/apt/lists/*

RUN poetry install --no-root

EXPOSE 5000

ENV FLASK_APP=src/app.py
ENV FLASK_RUN_HOST="0.0.0.0"
ENV FLASK_RUN_PORT="5000"
CMD ["poetry", "run", "flask", "run"]
