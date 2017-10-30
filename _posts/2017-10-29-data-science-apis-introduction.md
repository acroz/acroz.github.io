---
layout: post
title:  "Data Science APIs: Introduction"
date:   2017-10-29 19:26:00 +0000
categories: python api flask
summary: Machine learning has a lot of fantastic practical applications, but
         there comes a point where you want to package up your model so it can
         be used in practical applications. Web APIs provide a great mechanism
         to deploy and share models to the wider world.
series:
    name: "Data Science APIs"
    index: 1
---

You've developed a really great machine learning model to solve a difficult
data science problem, but now you want to wrap it in a convenient interface and
either share it with the world or integrate it smoothly into an application.
This series of blog posts addresses how to develop a web API to your model
using Flask, a Python web framework. I'll cover a bunch of suggestions along
the way to help make your API more robust and secure and how to get it up and
running in the wild.

In this first post, I'll start off by covering some of the concepts of APIs and
HTTP.

## Why API?

An Application Programming Interface (API) is a common concept in software
engineering. When using a library (for example to generate list the files in a
directory), you don't especially care how the library is implemented; all you
really need to know is that when you pass a directory path to `os.listdir()`,
it returns a list of files in that directory.

The same goes for code you develop yourself. When writing, for example, a web
frontend for your machine learning model, you ideally don't want to have to
know if the model code uses numpy arrays or pandas DataFrames for internal
storage. For this reason, you want to have a simple interface that defines a
clear contract between the model code and anything that calls it. This not only
makes development easier, but ensures different parts of the system are
decoupled, which generally makes them easier to maintain.

APIs can take multiple forms; the programmatic interface to a library of code
perhaps being the most common. However APIs can also involve communication
between different parts of a system by other means. In this blog post series
we're mainly focussed on web APIs over HTTP.

## Intro to HTTP

If you're unfamilar with the terminology of HTTP and the web, don't worry! This
section will introduce the basic concepts.

You may not be aware that you probably already make many web requests per day!
That's because making requests to web servers and rendering the responses is
the chief task of the web broswer you use on your laptop, phone or tablet. When
you type, say, `http://example.com/page` in your browser's address bar, it
first works out the address of the server corresponding to `example.com`, then
sends a request to `GET` the resource `/page` from that server:

![Client Server Model: Web]({{ "/public/data-science-apis/client_server_web.svg" | relative_url }}){:class="centered"}{:style="max-height: 150px;"}

The web server then returns some HTML to the browser in response to this
request (in this case simply the text 'Hello!'), which the browser renders and
displays.

The response also comes with a 'status code', in this case 200, which means
'OK', in other words that the request was handled successfully. Other status
codes can indicated various error conditions. You're probably familiar with one
of them, '404 NOT FOUND', which indicates that a requested resource does not
exist:

![Client Server Model: 404]({{ "/public/data-science-apis/client_server_web_404.svg" | relative_url }}){:class="centered"}{:style="max-height: 150px;"}

As well as different response codes, other HTTP methods than GET are available.
The one you are most likely to encounter in practical applications (and this
blog post series) is POST, which is generally used to create a resource on the
server:

![Client Server Model: POST]({{ "/public/data-science-apis/client_server_web_post.svg" | relative_url }}){:class="centered"}{:style="max-height: 150px;"}

Web servers hosting HTML content are great, but what does this mean for data
science APIs? Well, if we replace the browser in this scenario with some client
application which wants to interface with our machine learning model, and write
a web server that returns parsable structured data in response to web requests,
we can use HTTP as the mechanism to exchange data:

![Client Server Model: API]({{ "/public/data-science-apis/client_server_api.svg" | relative_url }}){:class="centered"}{:style="max-height: 150px;"}

Provided the client application knows how the response body is formatted, it is
able to make a call to the server any time it needs to make a prediction, and
then use the response prediciton as desired.

## Advantages of APIs using HTTP

It may not be immediately obvious why you'd want to provide an API over HTTP
rather than simply writing a library and interfacing with it locally. That may
be easier in the short term, but defining the interface over HTTP carries
several advantages:

1. It's language-agnostic. The client application does not have to be written
   in the same language as the model, giving more freedom to choose the best
   language for different parts of a larger system.
2. It allows easy sharing. Once you have your API server up and running, an
   HTTP interface means that you can give access to any client application that
   has access to the internet.
3. It detaches different parts of the system. Provided that the API
   specification does not change, the API server (and encapsulated model) and
   any client applications that call it can be updated and redeployed
   independently.
4. It facilitates horizontal scaling. You might have a lightweight web app that
   uses a model API with significant computational demands. If the interface is
   over HTTP, multiple replicas of the API server can be run, increasing its
   capacity without having to increase the number of replicas of the web app.

## Disadvantages of APIs using HTTP

There are some disadvantages to using HTTP:

1. Not having full control of the execution environment of the model denies the
   caller the ability to take advantage of any local computing resources they
   might have.
2. The possibility of network failure or latency is also very real, and
   interfacing over HTTP will likely be slower (though in many cases acceptably
   so) than interfacing with a native library.
3. Communication of sensitive data over the internet (and even private
   networks) must be done with care. Encrpytion is a must, and security attacks
   need to be guarded against.
4. There's an increased maintenance burden as additional servers or services
   need to be managed.
5. It's potentially much more difficult for client application developers to
   debug issues with the model code.

However, given these caveats, offering services, including machine learning
models, over web APIs is increasingly popular and is a great way to provide a
flexible interface to your models.
