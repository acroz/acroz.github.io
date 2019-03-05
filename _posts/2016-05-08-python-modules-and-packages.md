---
layout: post
title:  "Python Modules and Packages"
date:   2016-05-08 01:23:00 +0200
tags: [Python]
summary: Getting started with simple scripts in Python is really easy, but
         often we want to create reusable code in a larger project. Here we
         introduce python packages, and how to create them.
---

As a scripting language, one of the main benefits of Python is that you can just
open a file, write some code and simply execute it in short order. No functions,
no classes, just a few quick statements to solve a simple task. Great? Yeah...
but not always.

Very often, as in other programming languages, we want to write code for a
common task once and use it over and over. Wrapping this functionality in a
function is a great first step, but what if you want to reuse the same code in
many different scripts? That's where modules and packages come in.

## Modules

Python modules are really simple - basically, each file of Python source code is
a module, and you can import each of these modules into any other script. Say
you have a Python source file called `parser.py` that looks like:

{% highlight python %}
# parser.py

def load(filename):
    """
    Load data from a file where each line is one integer.
    """

    data = []

    with open(filename) as fp:
        for line in fp:
            data.append(int(line.strip()))

    return data
{% endhighlight %}

We can then use the functionality of this module using the `import` syntax.
When you attempt to import a module, it first searches in the current directory
for a Python source file of that name (`file.py` in the case of `import file`),
so the following file executed in the same directory as `parser.py` above will
use its load function to read 'datafile.txt' and print it:

{% highlight python %}
import parser

file_data = parser.load('datafile.txt')

for value in file_data:
    print(value)
{% endhighlight %}

Note the use of the dot `.` syntax to access the `load` function from `parser`.
In Python, modules behave just like other objects, and so you can access their
attributes as you would an attribute of the class.

It's important to realise that all code in the file will be executed when it's
first imported. Generally speaking you would only define functions, classes and
constant variables in modules you expect to be imported, but there are
expections to that that are outside the scope of this post.

### Importing from Other Locations

If you're reading this post, the chances are that you're already familiar with
the `import` syntax and have used it to import modules from the Python standard
library. For example, a common task is to read arguments from the command line
when executing a Python script:

{% highlight python %}
# times10.py

import sys

# Read the first command line argument
number = int(sys.argv[1])

print(number * 10)
{% endhighlight %}

The above script uses the `sys` module from the standard library to access the
command line arguments given to Python. The module need not be located in the
same directory, but is instead loaded from the Python path, a list of
directories in which to search for Python modules when importing.

Adding new modules to the Python path requires either copying them to a
directory already in the path, or by modifying the path to include its location.
The best way to handle this is through the use of a setup script, which will be
the subject of later posts.

## Packages

Writing reusable code in modules is a great feature in Python, however modules
containing a lot of functionality quickly get long and unwieldy. Fortunately, we
can put a collection of related Python files in a single Python package.

Packages are in essence special directories containing Python source files. What
tells Python that a directory is a package is the presence of a special file
called `__init__.py`. The easiest way to explain is with an example - consider
the following layout of files:

{% highlight none %}
code
├── mypackage
│   ├── __init__.py
│   ├── one.py
│   ├── two.py
│   └── three.py
├── other
│   └── other.py
└── script.py
{% endhighlight %}

In this setup, `mypackage` is a package, and `other` is not. If, in script.py,
we do any of:

{% highlight python %}
import mypackage.one
from mypackage import two
from mypackage.three import somefunc
{% endhighlight %}

Then we will be able to use the functionality in these modules of `mypackage`
(assuming `somefunc` is defined in `three.py`). On the other hand, any of the 
following lines with result in an `ImportError`:

{% highlight python %}
import other.other
from other import other
from other.other import somefunc
{% endhighlight %}

The only difference is that `__init__.py` is present in `mypackage`. This file
just needs to exist - it does not need to contain anything.

You can also nest packages, though each level needs to contain an `__init__.py`,
for example in the following structure:

{% highlight none %}
code
└── mypackage
    ├── subpackage
    │   ├── __init__.py
    │   └── four.py
    ├── __init__.py
    ├── one.py
    ├── two.py
    └── three.py
{% endhighlight %}

we can access modules in the subpackage with any of:

{% highlight python %}
import mypackage.subpackage.four
from mypackage.subpackage import four
from mypackage.subpackage.four import somefunc
{% endhighlight %}

### Advanced Use of `__init__.py`

While it's true that `__init__.py` does not need to contain anything, it can be
useful to do so. Importantly, when you import the package directly, for example
with the above structures:

{% highlight python %}
import mypackage
{% endhighlight %}

the code in `mypackage/__init__.py` will define the contents of the imported
`mypackage` module. This can be useful for designing a simple API to your
project, so instead of a user of the package needing to know that the function
`myspecialfunction` is in the module `mypackage.three`, the `__init__.py` could
have:

{% highlight python %}
from mypackage.three import myspecialfunc
{% endhighlight %}

End users can then simply run `mypackage.myspecialfunc` after importing
`mypackage` as above. There are a lot of ways of customising the import
mechanics of a package using `__init__.py` to suit your needs, but hopefully
this post gives you a taste of the possibilities!
