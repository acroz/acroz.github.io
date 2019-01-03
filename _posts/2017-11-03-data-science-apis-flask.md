---
layout: post
title:  "Data Science APIs: Flask"
date:   2017-11-03 14:38:00 +0000
categories: python api flask
summary: Flask is a great lightweight web framework for Python that makes it
         really easy to put together an API for a data science model quickly.
         In this post, I cover some of the basics for getting started with
         Flask and serving your model with a web API.
series:
    name: "Data Science APIs"
    index: 2
---

Perhaps the greatest strength of Python is the wide spectrum of libraries
available for it. Not only does it have a rich set of data processing tools and
machine learning libraries, but it is also widely used in web programming,
having a number of mature web frameworks available. This general purpose sets
it apart from other languages used in data science, and puts us in a great
place for productionising models as web APIs.

In this series of posts, I provide a guide for wrapping data science models in
web APIs using the [Flask] web framework. Flask is a great choice for this as
it is extremely lightweight, requiring only a little code to convert a Python
function into a web endpoint.

Other frameworks, like Django, are great, providing a lot of functionality out
of the box. However, much of this functionality is centred around implementing
fully fledged web applications rendering and serving HTML rather than providing
simple web APIs.

In this post, I'll cover the basics of [Flask], and wrap an example model from
[scikit-learn] into a simple API.

## Flask Basics

[Flask] is often referred to as a _microframework_ since it's very minimal.
Compared toother frameworks it provides only a core set of features needed to
implement HTTP endpoints, and it needs very little boilerplate. A minimal Flask
application looks like the following:

```python
from flask import Flask

app = Flask(__name__)

@app.route('/')
def hello():
    return 'Hello World!'

if __name__ == '__main__':
    app.run(debug=True)
```

In the above snippet, we instantiate the `Flask` app as `app`, then use the
`@app.route()` decorator to register the `hello()` function as an endpoint on
`/`, the root endpoint. Finally, we run the app with `app.run()`, in debug
mode.

Running the app is as simple as running the script:

```bash
$ python app.py
```

And while it's running, we can use `curl` to hit the server on the root
endpoint (on the default Flask port of 5000, which should be indicated in the
log of the app ran above):

```bash
$ curl localhost:5000
Hello World!
```

You can see that `curl` prints the body that was returned by the registered
endpoint, `Hello World!`.

You can also call the endpoint from any language's HTTP client library. In
Python, I'd recommend the [requests] library, which is not in the standard
library but is very widely used. This code snippet performs the same request as
above:

```python
>>> import requests
>>> response = requests.get('http://localhost:5000')
>>> response.text
'Hello World!'
```

You may prefer to use a GUI tool to run test queries against your API. One that
I've used and can recommend is [Postman], which has a lot of nice features.

## Adding Additional Routes

Aside from for the simplest applications, you'll want to expose multiple entry
points into your API. To do this, you can use the `@app.route()` decorator to
register different Python functions on different HTTP endpoints. Recall that
from the example above we registered our `hello()` function on the root
endpoint, `/`:

```python
@app.route('/')
def hello():
    return 'Hello World!'
```

The first argument to `@app.route()` determines the route the endpoint will be
served on. We can easily register additional functions on other endpoints:

```python
@app.route('/foo')
def foo():
    return 'bar'
```

You can easily choose the right endpoint by including it in the URL:

```bash
$ curl localhost:5000
Hello World!
$ curl localhost:5000/foo
bar
```

You can also parameterise endpoints with variable rules. Use angle brackets in
the route name to match any string and pass it as an argument to the function:

```python
@app.route('/hi/<name>')
def hi(name):
    return f'Hi {name}!'
```

This can again be queried by choosing the right URL:

```bash
$ curl localhost:5000/hi/Andrew
Hi Andrew!
$ curl localhost:5000/hi/acroz
Hi acroz!
```

## Encoding Responses in JSON

In the examples given so far, we've generated some fairly simple text as output
in order to demonstrate the routing functionality in Flask, however for a
practical data science API you'll typically want to return more rich structured
and/or numerical data. There are a numer of different ways you can encode this
information, but the most common is to use _JavaScript Object Notation_, or
JSON for short.

JSON is a great choice for APIs as it's simple, yet provides enough to cover
most use cases; it's easy to parse, yet is fairly human-readable; practically
every language has a parser, so you don't need to write one yourself; and it's
so commonly used in APIs that it's practically a standard.

Python has JSON support in its standard library, but when using Flask I
recommend using the `jsonify()` helper, which not only serialises your data to
JSON, but prepares a Flask `Response` object with useful things like the HTTP
content type preset.

To use `jsonify()`, pass the Python object (usually a `dict`) you want to
endcode, and return the generated response:

```python
from flask import jsonify

@app.route('/api')
def api():
    data = {
        'name': 'Andrew',
        'user': 'acroz'
    }
    return jsonify(data)
```

You can then query the endpoint as normal:

```bash
$ curl localhost:5000/api
{
  "name": "Andrew",
  "user": "acroz"
}
```

As mentioned, a lot of languages and libraries have JSON support built in. The
Python [requests] library I demonstrated earlier is among them. Call `.json()`
on a requests response object to decode the body as JSON and return the
equivalent Python representation:

```python
>>> response = requests.get(
>>>     'http://localhost:5000/api'
>>> )
>>> response.json()
{'name': 'Andrew', 'username': 'acroz'}
```

### Jsonifying NumPy Values

It's worth noting that Python's standard library `json` package, which is used
internally by `flask.jsonify()`, doesn't play nicely with NumPy types. For
example, while the serialisation of a normal Python `int` works fine:

```python
>>> import json
>>> json.dumps(3)
'3'
```

Doing the same with a `numpy.int64` does not:

```python
>>> import numpy
>>> json.dumps(numpy.int64(3))
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
  File "/Users/acroz/.pyenv/versions/3.6.2/Python.framework/Versions/3.6/lib/python3.6/json/__init__.py", line 231, in dumps
    return _default_encoder.encode(obj)
  File "/Users/acroz/.pyenv/versions/3.6.2/Python.framework/Versions/3.6/lib/python3.6/json/encoder.py", line 199, in encode
    chunks = self.iterencode(o, _one_shot=True)
  File "/Users/acroz/.pyenv/versions/3.6.2/Python.framework/Versions/3.6/lib/python3.6/json/encoder.py", line 257, in iterencode
    return _iterencode(o, 0)
  File "/Users/acroz/.pyenv/versions/3.6.2/Python.framework/Versions/3.6/lib/python3.6/json/encoder.py", line 180, in default
    o.__class__.__name__)
TypeError: Object of type 'int64' is not JSON serializable
```

For that reason, you'll want to make sure any content you're serialising with
`flask.jsonify()` is converted to native Python types. In the above example:

```python
>>> numpy_integer = numpy.int64(3)
>>> json.dumps(int(numpy_integer))
'3'
```

And for arrays:

```python
>>> array_1d = numpy.array([1., 1.5, 2.])
>>> json.dumps([float(v) for v in array_1d])
'[1.0, 1.5, 2.0]'
>>> array_2d = numpy.array([[1., 1.5], [1.5, 2.]])
>>> json.dumps([[float(v) for v in row] for row in array_2d])
'[[1.0, 1.5], [1.5, 2.0]]'
```

## Wrapping a Data Science Model

I've covered some of the basics of wrapping Python functionality in HTTP
endpoints using Flask; now I'll go through a brief example of a [scikit-learn]
model that I want to wrap in an API.

### Example Model

[scikit-learn] provides some convenient functions for generating training data
that you can use to test out models. I'm using `make_classification` from
`sklearn.datasets` to generate some data to fit a binary classifier to:

```python
from sklearn.datasets import make_classification

X, y = make_classification(
    n_samples=100,
    n_features=2,
    n_classes=2,
    n_informative=2,
    n_redundant=0
)
```

This generates two clusters in a 2-dimensional feature space:

![Training Data]({{ "/public/data-science-apis/logistic_data.svg" | relative_url }}){:class="centered"}

Using [scikit-learn], it's fairly easy to train a simple logsitic regression
classifier to this data:

```python
from sklearn.linear_model import LogisticRegression
model = LogisticRegression()
model.fit(X, y)
```

We can then use this trained classifier to predict the class of a point with a
value of 2 for both features:

```python
>>> import numpy
>>> X_predict = numpy.array([[2, 2]])
>>> model.predict(X_predict)
array([1])
```

We can also determine the probability of that point being of either class:

```python
>>> model.predict_proba(X_predict)
array([[ 0.02086766,  0.97913234]])
```

Plotting the line where both probabilities are 0.5 allows us to see the
decision boundary predicted by the model:

![Classifier]({{ "/public/data-science-apis/logistic.svg" | relative_url }}){:class="centered"}

### Model as an API

I now want to make the prediction functionality of this model to be exposed
through an API. Assuming that the trained model is available in the module
namespace as `model`, we can register a `/predict` endpoint with the Flask app
that takes the two features as inputs:

```python
@app.route('/predict/feature_1/<feature_1>/feature_2/<feature_2>')
def predict(feature_1, feature_2):

    # Convert inputs from strings to floats
    feature_1 = float(feature_1)
    feature_2 = float(feature_2)

    # Perform model prediction
    features = numpy.array([[feature_1, feature_2]])
    predicted_class = model.predict(features)[0]
    probabilities = model.predict_proba(features)[0]

    # Prepare response
    content = {
        'class': int(predicted_class),
        'probabilities': [
            float(p) for p in probabilities
        ]
    }

    return jsonify(content)
```

This example puts together the Flask features described above: the features are
extracted from the endpoint and passed as arguments to the function, used to
make a model prediction, and a JSON response is generated and returned.

We can then query the endpoint to do a model prediction:

```bash
$ curl localhost:5000/predict/feature_1/2.0/feature_2/2.0
{
  "class": 1,
  "probabilities": [0.02086766, 0.97913234]
}
```

There remain a number of improvements that can be made to this endpoint. For
example, consider what happens when either `feature_1` or `feature_2` passed to
`predict()` can't be converted to a valid float? In further blog posts, I'll
cover ways of guarding against such issues and provide examples covering more
complicated flows that you may wish to implement.

[Flask]: http://flask.pocoo.org/
[scikit-learn]: http://scikit-learn.org/
[requests]: http://python-requests.org/
[Postman]: https://www.getpostman.com/
