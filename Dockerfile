FROM python:3.12-slim

WORKDIR /app

#ARG SECRET_KEY
#ARG DATABASE_URL
#ARG LOGGER_LOCATION
#ARG LOGGER_TEST_LOCATION
#
#ENV SECRET_KEY=${SECRET_KEY}
#ENV DATABASE_URL=${DATABASE_URL}
#ENV LOGGER_LOCATION=${LOGGER_LOCATION}
#ENV LOGGER_TEST_LOCATION=${LOGGER_TEST_LOCATION}

COPY setup.py ./setup.py
COPY src ./src

RUN python -m pip install --upgrade pip \
 && python -m pip install .[test]

COPY tests ./tests

EXPOSE 5001

ENV PYTHONPATH=/app/src
ENV FLASK_ENV=development

CMD [ "python", "src/main.py" ]

# Käivitamine docker-compose.yml abil käsuga "docker-compose up --build -d"

# Build käsk: docker build -t books-be:latest .
# Käivitamine: docker run -d -p 5001:5001 -v $(pwd)/src:/app/src --env-file .env.dev --name books-be books-be:latest