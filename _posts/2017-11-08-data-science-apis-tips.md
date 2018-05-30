---
layout: post
title:  "Data Science APIs: Building Robust APIs"
date:   2017-11-08 23:09:00 +0000
categories: python api flask
series:
    name: "Data Science APIs"
    index: 3
---

In the previous post in this series, I covered the basics of building web APIs
with [Flask]. However, without a little care and attention, it's easy to
introduce some unpleasant bugs that could cause your API to fail in unexpected
ways or introduce serious security holes. In this blog post I'll provide a few
tips and tricks you can use to guard against these issues.

## JSON Error Handler

By default, [Flask] returns HTML-formatted pages when an error occurs trying to
fulfill a request. For instance, when an endpoint is requested that does not
correspond to anything known on the server, it returns the well known 404 error
response, which indicates 'Not Found' (for a full list of HTTP status codes
check out [httpstatuses.com](https://httpstatuses.com/)), with the following
content:

```html
<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 3.2 Final//EN">
<title>404 Not Found</title>
<h1>Not Found</h1>
<p>
  The requested URL was not found on the server. If you entered the URL
  manually please check your spelling and try again.
</p>
```

For the primary use case for [Flask], serving HTTP web pages, this is great, as
it returns something that a browser can display and show something meaningful
to the user. However, for an API expecting a JSON response it is less useful,
as any attempt to interpret the response as JSON will fail. For example, when
using [requests] to query a missing endpoint on a Flask server:

```python
>>> import requests
>>> response = requests.get('http://localhost:5000')
>>> response.status_code
404
>>> response.json()
Traceback (most recent call last):
  File "call.py", line 2, in <module>
    requests.get('http://localhost:5000').json()
  File "/home/acroz/.pyenv/versions/3.6.3/lib/python3.6/site-packages/requests/models.py", line 892, in json
    return complexjson.loads(self.text, **kwargs)
  File "/home/acroz/.pyenv/versions/3.6.3/lib/python3.6/json/__init__.py", line 354, in loads
    return _default_decoder.decode(s)
  File "/home/acroz/.pyenv/versions/3.6.3/lib/python3.6/json/decoder.py", line 339, in decode
    obj, end = self.raw_decode(s, idx=_w(s, 0).end())
  File "/home/acroz/.pyenv/versions/3.6.3/lib/python3.6/json/decoder.py", line 357, in raw_decode
    raise JSONDecodeError("Expecting value", s, err.value) from None
json.decoder.JSONDecodeError: Expecting value: line 1 column 1 (char 0)
```

Instead, we'd like to configure [Flask] to always return JSON. To do this,
first make a function that creates a flask `Response` for a given Python
exception:

```python
from werkzeug.exceptions import HTTPException, InternalServerError

def json_errorhandler(exception):
    """Create a JSON-encoded flask Response from an Exception."""

    if not isinstance(exception, HTTPException):
        exception = InternalServerError()

    response = jsonify({
        'error': exception.name,
        'description': exception.description
    })
    response.status_code = exception.code

    return response
```

Note that the `HTTPException` class from `werkzeug` is the exception type used
by [Flask] to represent HTTP failure cases, like 404 above. Any other Python
exception being passed here indicates that an exception was raised while
handling a request, and we therefore convert to an `InternalServerError`, which
returns the corresponding 500 status response.

It's then a simple matter to register the function as the error handler:

```
from werkzeug.exceptions import default_exceptions

for code in default_exceptions.keys():
    app.register_error_handler(code, json_errorhandler)
```

Now error messages are formatted with JSON by default. Requesting a missing
endpoint as in the example above will return a JSON encoded body containing a
descriptive error message:

```json
{
  "error": "Internal Server Error",
  "description": "The requested URL was not found on the server.  If you entered the URL manually please check your spelling and try again."
}
```

This can now be read reliably by [requests]:

```python
>>> import requests
>>> response = requests.get('http://localhost:5000')
>>> response.status_code
404
>>> response.json()
{'error': 'Internal Server Error', 'description': 'The requested URL was not found on the server.  If you entered the URL manually please check your spelling and try again.'}
```

## Malformed Inputs

Another issue you might come across is badly formatted inputs. Looking back at
[the example from the previous post in this series
]({% post_url 2017-11-03-data-science-apis-flask %}#model-as-an-api), consider
what happens to the arguments passed to the function as `feature_1` and
`feature_2`. They first get passed to `float()`:

```python
feature_1 = float(feature_1)
feature_2 = float(feature_2)
```

In the case that the passed strings can be converted to floats, this will work
well, however when something like `'invalid'` is passed, it will raise a
`ValueError`. This exception is not caught inside our API function, and so
Flask catches it and returns a 500 Internal Server Error to the client.

This isn't a great experience, since there's no indication to the caller why
failure occurred, and worse still, it implies that the failure was due to some
mistake in the code rather than because of bad inputs being provided.

To correct this, you should catch the `ValueError` and use [Flask]'s `abort`
helper function to exit from the function early and return a 400 HTTP response
to the caller, indicating a 'Bad Request'. The example above then becomes:

```python
from flask import abort

@app.route('/predict/feature_1/<feature_1>/feature_2/<feature_2>')
def predict(feature_1, feature_2):

    # Convert inputs from strings to floats
    try:
        feature_1 = float(feature_1)
        feature_2 = float(feature_2)
    except ValueError:
        abort(400, 'Input features were not valid floats')

    # Model prediction code ...

    return jsonify(content)
```

You could also check that the inputs are vaild explicitly before attempting the
conversion, however Pythonic style usually prefers trying to perform a type
conversion first and catching the exception in the case that it failed.

So now, when calling the client with [requests], instead of the generic 500
response received previously:

```python
>>> endpoint = '/predict/feature_1/1.0/feature_2/invalid'
>>> response = requests.get(f'http://localhost:5000{endpoint}')
>>> response.status_code
500
>>> response.json()
{'error': True, 'message': 'Internal server error'}
```

We now get a response with a much more approriate status code and a useful
error message:

```python
>>> endpoint = '/predict/feature_1/1.0/feature_2/invalid'
>>> response = requests.get(f'http://localhost:5000{endpoint}')
>>> response.status_code
400
>>> response.json()
{'error': True, 'message': 'Input features were not valid floats'}
```

### Variable Rules

If you're familiar with [Flask], you may be aware that it provides some
functionality for validating URL parts match certain formats, called [variable
rules]. It's a nice feature that avoids writing boilerplate code, however be
careful of the float converter - at the time of writing, it doesn't support
negative values.

## SQLAlchemy

In [my model example in the previous post in this series
]({% post_url 2017-11-03-data-science-apis-flask %}#example-model), I trained
my classifier to some sample data generated with [scikit-learn], however in a
useful model you'll want to train it to some real data of significance. It's
good practice to keep such data in a proper database for peristence, rather
than keeping state in memory, which will be lost when the application restarts,
or by managing some custom text files, which can be error prone.

SQL databases are most common for this kind of task, especially when dealing
with tabular data, and the most common library for interacting with them is
[SQLAlchemy]. I'm not going to give a tutorial here on how to interact with
databases with SQLAlchemy, but to give you an idea of a typical use case, here
is that same model trained to data read from a PostgreSQL database:

```python
import pandas
import sqlalchemy

# Create connection with database
DATABASE_URL = 'postgres://localhost/postgres'
engine = sqlalchemy.create_engine(DATABASE_URL)
connection = engine.connect()

# Read query result directly into a pandas dataframe
query = 'SELECT * FROM data'
data = pandas.read_sql(query, connection)

# Train the model
features = numpy.array(data[['feature_1', 'feature_2']])
classes = numpy.array(data['class'])
model = LogisticRegression()
model.fit(features, classes)
```

### Integration with Flask

SQLAlchemy needs some configuration to manage its connection pool and session
in an optimal way for an HTTP request context; if managed improperly, stale
database connections could accumulate and result in an application failure.

Rather than setting up this configuration yourself, I recommend using
[Flask-SQLAlchemy], which does it for you. To set it up:

```python
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = \
    'postgres://localhost/postgres'
db = SQLAlchemy(app)
```

You can then use `db.engine` as the connection object with `pandas.read_sql()`.
In the above example, run:

```python
data = pandas.read_sql(query, db.engine)
```

### Guarding against SQL Injection

Constructing SQL queries from API endpoints is dangerous, as demonstrated by
[a well known xkcd strip][xkcd Bobby Tables]:

![xkcd Bobby Tables](https://imgs.xkcd.com/comics/exploits_of_a_mom.png){:class="centered"}

If you were to execute a SQL query constructed from some input provided for a
user, it would be possible for a caller to delete all your data, as in this
xkcd comic. Constructing queries by normal Python string interpolation is
therefore not a good idea:

```python
connection.execute(
    f'SELECT * FROM some_table WHERE name = "{user_input}"'
)
```

It's easy to guard against this by simply using SQLAlchemy's query
interpolator, which sanitises any provided data:

```python
connection.execute(
    'SELECT * FROM mytable WHERE name = :name',
    name=name
)
```

Using the suggestions and tips provided in this post, you'll be able to write
APIs in Flask which are more robust and secure. In the next post in this
series, I'll show how to handle longer running calculations effectively in your
API.

[Flask]: http://flask.pocoo.org/
[scikit-learn]: http://scikit-learn.org/
[requests]: http://python-requests.org/
[variable rules]: http://flask.pocoo.org/docs/latest/quickstart/#variable-rules
[SQLAlchemy]: https://www.sqlalchemy.org/
[Flask-SQLAlchemy]: http://flask-sqlalchemy.pocoo.org/
[xkcd Bobby Tables]: https://xkcd.com/327/
