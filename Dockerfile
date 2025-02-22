FROM python:3.12-slim

RUN pip install poetry==2.1.1

WORKDIR /app

COPY pyproject.toml poetry.lock ./
COPY . .

RUN poetry install --no-root

EXPOSE 5000

ENV FLASK_APP=App/run.py
ENV FLASK_RUN_HOST="0.0.0.0"
ENV FLASK_RUN_PORT="5000"

CMD ["poetry", "run", "flask", "run"]
