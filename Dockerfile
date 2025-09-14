FROM python:3.12-slim

WORKDIR /books-be

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p /books-be/logs

EXPOSE 5001

# Otsib mooduleid ja pakette
ENV PYTHONPATH=/books-be/src
# Töötab debug mode-s, automaatne koodi reload (ei pea restartima konteinerit iaga muudatuse järel)
ENV FLASK_ENV=development

CMD [ "python", "src/main.py" ]

# Käivitamine käsuga: docker run -d -p 5001:5001 -v $(pwd)/logs:/books-be/logs -v $(pwd)/src:/books-be/src --name books-be books-be:v1.1