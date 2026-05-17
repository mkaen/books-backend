FROM python:3.12-slim

WORKDIR /app

#ARG SECRET_KEY
#ARG DATABASE_URL
#ARG LOGGER_LOCATION
#ARG LOGGER_TEST_LOCATION
#ARG ENVIRONMENT

#ENV SECRET_KEY=${SECRET_KEY}
#ENV DATABASE_URL=${DATABASE_URL}
#ENV LOGGER_LOCATION=${LOGGER_LOCATION}
#ENV LOGGER_TEST_LOCATION=${LOGGER_TEST_LOCATION}

COPY setup.py pyproject.toml* wsgi.py ./
COPY src ./src

RUN python -m pip install --upgrade pip \
 && python -m pip install '.[prod]'

COPY tests ./tests

ENV PYTHONPATH=/app

EXPOSE 5001

CMD [ "gunicorn", "--bind", "0.0.0.0:5001", "--workers", "2", "--access-logfile", "-", "--error-logfile", "-", "wsgi:app" ]