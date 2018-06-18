---
layout: post
title:  "Data Science APIs: Long Running Tasks"
date:   2018-01-07 15:55:00 +0000
categories: python api flask
series:
    name: "Data Science APIs"
    index: 4
---

Data science models often require longer running computations for training or
predicion, but HTTP requests that take longer than a few seconds to respond are
at increased risk of failure. In this post, I'll show you how to handle longer
running tasks in your API with [RQ].

## RQ

[RQ] (Redis Queue) is a simple job queue library for Python. The idea with job
queue systems is that you have dedicated worker processes which consume tasks
from a shared queue, which the main application process can insert tasks into.
In the case of an API server, this allows the main process to insert a long
running task into the queue and return immediately, rather than blocking until
the task is complete and risking connection failure.

To use [RQ], put a function defining your task in a separate module from your
main application code (so it is easily importable by the workers):

```python
# tasks.py
import time

def slow_multiply(x, y):
    time.sleep(10)
    return x * y
```

Then, in your main code, create an [RQ] queue using [Redis] as the queue store,
and submit tasks to it with `enqueue()`:

```python
# main.py
from redis import Redis
from rq import Queue
import tasks

queue = Queue(connection=Redis())

x = 2
y = 3
queue.enqueue(tasks.slow_multiply, x, y)
```

For your application to run, you'll need to install and run the [Redis] server
separately, in addition to running one or more [RQ] workers with:

```bash
$ rq worker
```

## POST/GET Example with Flask

You'll usually want to get the result of a long running task back, however if
some API code executed when handling a request submits a job into the queue and
returns immediately, the caller will not know the result.

A common model to get results back from the API in this case is for it to
return a task ID to the client that it can then use to query for the result
later. The sequence of events looks like:

1. The client sends a request to the API to perform a task.
2. The API server generates a unique task ID, submits the task and ID to the
   queue, and returns the ID to the client.
3. A worker will pop the task off the queue, perform it, then insert the result
   into a database with the ID provided.
4. In the meantime, the client sends a request with the task ID to the API,
   which initially responds to say no result is available. The client retries
   this request at a fixed interval.
5. Once the result is available in the database, the next time the client
   queries for the result, it is retrieved and returned to the client.

Below is a minimal [Flask] example implementing this model for my trivial
`slow_multiply()` task above:

`core.py` provides objects required by both the Flask app and the workers:

```python
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from rq import Queue
from redis import Redis

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = \
    'postgresql://username:password@host:port/database'
db = SQLAlchemy(app)
queue = Queue(connection=Redis())
```

`tasks.py` implements the long running task, writing the result into the
database when done:

```python
import time
from core import db

def slow_multiply(task_id, x, y):
    time.sleep(10)
    result = x * y
    db.engine.execute(
        'INSERT INTO results (task_id, result) ' +
        'VALUES (:task_id, :result)',
        task_id=str(task_id), result=result
    )
```

`views.py`, implements the endpoints on the Flask app:

```python
import uuid
from core import app, db, queue
from tasks import slow_multiply

@app.route('/multiply', methods=['POST'])
def submit_multiplication():
    """Queue a multiplication and return the task ID."""
    body = request.get_json(force=True)
    task_id = uuid.uuid4()  # new unique id
    queue.enqueue(
        slow_multiply,
        task_id, body['x'], body['y']
    )
    return jsonify({'task_id': str(task_id)}), 202

@app.route('/multiply/<task_id>', methods=['GET'])
def get_multiplication(task_id):
    """Return the result for a task ID, if completed."""
    query_result = db.engine.execute(
        'SELECT result FROM results WHERE task_id = :task_id',
        task_id=task_id
    ).first()
    if query_result is None:
        abort(404)
    else:
        return jsonify({'result': query_result[0]})

if __name__ == '__main__':
    app.run()
```

To run this app, you'll need to run a [Redis] server locally, run the [Flask]
app with `python views.py`, and run one or more [RQ] workers. However, since
the workers now use the Flask-SQLAlchemy `db` object, the workers need to be
run in the Flask application context. The following snippet is all you need for
this:

```python
from rq import Connection, Worker
from core import app, queue

with app.app_context():
    with Connection():
        w = Worker([queue])
        w.work()
```

### Example Client Code

To submit a multiplication task to be executed by the workers, submit a POST to
the `/multiply` endpoint with the expected JSON body:

```python
>>> import requests
>>> response = requests.post(
>>>     'http://your-api.com/predict',
>>>     json={'x': 2.3, 'y': 2.0}
>>> )
>>> response.status_code
202
```

The body of the response includes the task ID:

```python
>>> response.json()
{'task_id': '6ba6be8e-ed13-4216-9959-2edcf08dd8f0'}
```

This can then be used to check if the result is ready:

```python
>>> task_id = response.json()['task_id']
>>> url = f'http://your-api.com/predict/{id}'
>>> response = requests.get(url)
>>> response.status_code
404
```

Once the result is ready, the status code will be 200 and not 404:

```python
>>> response = requests.get(url)
>>> response.status_code
200
>>> response.json()
{'result': 4.6}
```

[RQ]: http://python-rq.org/
[Redis]: https://redis.io/
[Flask]: http://flask.pocoo.org/
