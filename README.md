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
```
pip install .[test]
```

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
