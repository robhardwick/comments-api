# Comments API

A simple API to allow creation and viewing of comments. All comments are subject to sentiment analysis by the [Watson Tone API](https://www.ibm.com/watson/services/tone-analyzer/).

## Dependencies

* Python 3.x
* PostgreSQL 9.6.x
* RabbitMQ 3.6.x
* Redis 3.2.x

## Development Setup

1. Ensure PostgreSQL, RabbitMQ and Redis are running

2. Create a new database and user in PostgreSQL:

```
CREATE DATABASE commentsapi;
CREATE USER commentsapi WITH PASSWORD 'commentsapi';
ALTER ROLE commentsapi SET client_encoding TO 'utf8';
ALTER ROLE commentsapi SET default_transaction_isolation TO 'read committed';
ALTER ROLE commentsapi SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE commentsapi TO commentsapi;
```

3. Create virtualenv:

```
virtualenv --python=$(which python3) venv
```

4. Install dependencies:

```
. venv/bin/activate
pip install -r requirements.txt
```

5. Initialise database:

```
python manage.py migrate
```

6. Create super user:

```
python manage.py createsuperuser
```

7. Run server:

```
python manage.py runserver
```
