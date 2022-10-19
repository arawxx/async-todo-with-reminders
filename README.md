# Asynchronous Todo app with async reminding functionality using Telegram bots (Backend-side)


## Technologies used:
- FastAPI for API
- PostgreSQL for database
- Async SQLAlchemy as the ORM coupled with Alembic for migrations
- Aiogram for using _a previously created_ telegram bot (used for sending OTPs and reminding user's todos)

- Celery for task scheduling
    - Redis as Celery's results Backend
    - RabbitMQ as the message Broker between the App and Celery
---

## Requirements

### Telegram Bot
Using @BotFather in Telegram, first create a bot and go through configuring it _(BotFather will guide you, __making you an offer you can't refuse ;}__ )_. You will be given a Token in the end. Set this token inside your `.env` file.

### Environment Variables
You also need to create a single `.env` file and specify the below required environment variables:

##### PostgreSQL
- `POSTGRES_USER`
- `POSTGRES_PASSWORD`
- `POSTGRES_DB`

##### pgAdmin
- `PGADMIN_DEFAULT_EMAIL`
- `PGADMIN_DEFAULT_PASSWORD`

##### FastAPI
- `DB_URL`
- `SECRET_KEY`
- `ALGORITHM`
- `TOKEN_EXPIRATION_IN_SECONDS`

##### Celery
- `BROKER_URL`
- `BACKEND_URL`

Note: Put these all inside one file named `.env`

Note: If launching without Docker, you need to first load the environment variables, e.g. using `dotenv` module's `load_dotenv()` method

Note: `Secret_key` and `Algorithm` are used for login token handling

### Docker
It's highly recommended to launch this using [Docker](https://www.docker.com).

Otherwise you are gonna have to install different applications, and use two seperate terminals for launching the app. (one for FastAPI and one for the Celery worker)


---

## Finally (using Docker)
Use `docker-compose up` command to launch the application.

## Otherwise (not using Docker)
After setting up PostgreSQL, Redis and RabbitMQ:
### in one terminal
run `uvicorn main:app`
### in another terminal
on _Linux / MacOS_, run: `celery -A utils.celery_worker.app worker --loglevel=info`

on _Windows_, run: `celery -A utils.celery_worker.app worker --pool=solo --loglevel=info`

---
## Finally (for real)
Check out `localhost:8000` for FastAPI, and its docs (_Swagger_) at `localhost:8000/docs`

___Using Docker only___ access pgAdmin at `localhost:5050`