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

7. Run celery:

```
celery -A comments worker -l info
```

8. Run server:

```
python manage.py runserver
```

9. Browse to [http://localhost:8000](http://localhost:8000)

## Discussion

### Overview

The majority of the project functionality is stored in the following files:

* [models.py](comments/api/models.py)
* [tasks.py](comments/api/tasks.py)

Due to the length of time spent on the project there are a number of pieces of functionality missing that would need to be developed to bring it up to production standard:

* No example client was developed. It would be good to include a basic Javascript client to demonstrate how the API should be used. In lieu of this the [test suite](comments/api/tests.py) and API documentation should be consulted.
* The caching system is very basic and simply uses the default Django caching middleware. When the background task finishes it currently clears the *entire* site cache which has an extremely negative impact on performance!
* No authentication or authorisation is performed by the API.
* Only a basic test suite has been included. It would be good to test more failure cases for both the API methods and the background task. Additionally, it would be nice to include some basic performance testing to ensure there are no performance regressions during future development.
* The use of a relational database may or may not be ideal depending on the scale of deployment and what additional features, if any, are required.
* Server provisioning and deployment has not been considered. It would be good to define this alongside the code (e.g. with Ansible playbooks).

### Scaling

In order to operate at scale the project has been separated into the following services:

* API (Django)
* Data store (PostgreSQL)
* Cache (Redis)
* Task queue (RabbitMQ)
* Task workers (Celery)

Each of these services could be deployed to multiple servers, with additional servers added as demand increased. The only service which would require effort to scale is PostgreSQL but this could still be achieved in a number of ways (e.g. partitioning/sharding or by adding replicas). It may prove more efficient to use a document store instead of a relational database depending on the ratio of reads to writes and if any sort of real-time aggregation was needed.

In addition, this structure allows each service to be swapped out with relative ease should they prove to be unsuitable in practice or if requirements were to change.

### REST

The API is built with the principles of REST in mind, specifically:

* Client-Server - The API is built such that all resource concerns (i.e. fields, types) are handled by the server and any user interface concerns are at the discretion of the client.
* Stateless - Each operation supported by the API is idempotent so that the multiple requests will achieve the same result. This is achieved by proper usage of the HTTP verbs so that GET always returns the current state of a comment, POST always creates a new comment, PUT always replaces a comment, PATCH always updates a comment and DELETE always removes a comment.
* Cache - The API supports caching by intermediaries between the server and the client (such as proxy servers) by proper use of HTTP verbs. This means that a GET request will never change any state on the server so it may be cached where as a POST request will create a new comment and so many not be cached.
* Uniform Interface - The API behaves in a consistent way (largely achieved through the Django REST Framework library). Each resource is added, edited, viewed and deleted through requests to a single URI. Each resource contains the information required to manipulate it (e.g. a single GET request contains all the information needed to update or delete it). The requests and resources are self-descriptive so the server honours the `Accept` header and the client honours the `Content-type` header where possible. The API adheres to the [HATEOAS](https://en.wikipedia.org/wiki/HATEOAS) principle by allowing dynamic discovery of all aspects of the API by recursively following the URLs provided in the API root.
* Layered System - The design of the API is such that any number of intermediaries may be placed between the client and server. This makes it easy, for example, to add caches or load-balancers on the server side or for the client to use proxies.
* Code-on-demand - This has not been implemented for this API as it serves no purpose given the current requirements.

### Structure

The code is structured using the standard Django conventions so models are separated from views and the views are separated from the URLs. Additionally, processes that are longer running have been separated into tasks which is a very common pattern in scaleable and performant systems.

For developers familiar with Django a brief discussion on the aims of the project along with the knowledge that the code follows Django conventions should be enough to onboard them to the project. For developers who haven't used Django before it would also be necessary to explain the Django code conventions and how these relate to more general programming patterns such as MVC.

### Documentation

The API has been documented using the [built-in Django REST framework documentation](http://www.django-rest-framework.org/topics/documenting-your-api/) which pulls in comments from the code to describe the available requests. Additionally, the adherence to REST principles coupled with the browsable HTML interface provided by Django REST framework allows developers to play with the API to understand how it works.
