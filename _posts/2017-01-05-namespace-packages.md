---
layout: post
title:  "Python Namespace Packages"
date:   2017-01-05 22:25:00 +0000
tags: [Python]
summary: Sometimes it's useful to split the components of a Python library
         across multiple respositories, but still access them from the same
         namespace. Namespace packages are a great mechanism for achieving
         this.
---

Suppose you have a great Python library called `mylib` (I really hope you pick
better package names than I do), but you have some additional feature that you
don't want to maintain in the same repository, but should be accessible through
`mylib`. Namespace packages provide a great mechanism for doing this, which I
will explain in this blog post.

In our `mylib` example, there is a core package with the main code:

```
mylib
├── mylib
│   ├── __init__.py  <-- top level __init__.py
│   ├── code.py
│   └── core
│       ├── __init__.py
│       └── code.py
└── setup.py
```

and also a second package which provides a `plugin` subpackage:

```
mylib-plugin
├── mylib
│   ├── __init__.py  <-- top level __init__.py
│   └── plugin
│       ├── __init__.py
│       └── code.py
└── setup.py
```

Note, however, that neither of these packages is the 'master' one - they can be
used together or completely in isolation.

If both of these packages were installed to a system and they did not use the
namespace package mechanism, at module import time only the one found first
would be imported, and the subpackages from the other one would be
inaccessible. So, in this example, if the main package was found first, the
plugin would be inaccessible, and vice versa.

Namespace packages overcome this by providing a hint to the import mechanism
that it should keep searching for other packages of the same name before
attempting to load any subpackages. This is done by making the top level
package `__init__.py` files consist of exactly the single line:

{% highlight python %}
__import__("pkg_resources").declare_namespace(__name__)
{% endhighlight %}

## `setuptools`

You'll also need to indicate to `setuptools` in your `setup.py` installation
script that `mylib` is a namespace package. This is done with the
`namespace_packages` keyword argument:

{% highlight python %}
# mylib/setup.py
from setuptools import setup, find_packages

setup(
    name='mylib',
    version='1.3.7',
    namespace_packages=['mylib'],
    packages=find_packages()
)
{% endhighlight %}

and similarly, in the plugin package:

{% highlight python %}
# mylib-plugin/setup.py
from setuptools import setup, find_packages

setup(
    name='mylib.plugin',
    version='0.2.2',
    namespace_packages=['mylib'],
    packages=find_packages()
)
{% endhighlight %}

## Limitations

Because the top level package needs to indicate that it's not a real package to
the import mechanism, it can't have code in its top level `__init__.py`. For
most applications, however, this is not a big problem.
