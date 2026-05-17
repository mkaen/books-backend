# Books-backend

## About application
Application provides for registered users to upload their books for borrowing to another users for free.


### ADD ENVIRONMENT VARIABLES
#### .env
```
SECRET_KEY="XXXXXXXXXXXXXXXXXXXXXX"
DATABASE_URL="postgresql://XXXXXXXX@XXXXXXXX:5432/postgres"
```

### SETUP LOCALLY & INSTALL DEPENDENCIES
```bash
python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -e '.[test]'
```

Run tests:
```bash
pytest
```

Run the API locally from the **project root** (`books-backend/`, where `setup.py` is):

```bash
flask run
```

Alternative: `python -m src.main` or `make run`

`.flaskenv` sets `FLASK_APP`, port `5001`, and `PYTHONPATH` so `flask run` works without extra flags.

On zsh, quote the extras so the shell does not treat `[test]` as a glob: `'.[test]'`.

### DATABASE
Set up database and create tables using postgres:
```
alembic upgrade head
```

### DOCKER
Build and run container using docker compose
```
docker compose up -d
```
