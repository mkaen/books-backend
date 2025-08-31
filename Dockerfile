FROM python:3.12-slim

WORKDIR /books-be

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p /books-be/logs

EXPOSE 5001

ENV PYTHONPATH=/books-be/src
ENV FLASK_ENV=development

CMD [ "python", "main.py" ]