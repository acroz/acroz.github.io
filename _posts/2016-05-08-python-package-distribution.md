---
layout: post
title:  "Python Package Distribution"
date:   2016-05-08 14:13:00 +0200
tags: [Python]
summary: You've written a great Python package and want to share it with the
         world. But how should you go about that? Here we discuss how to
         distribute your project in a way that allows other Python users to use
         your code as easily as possible.
---

In a [previous post][modpkg], I introduced the basics of Python modules and
packages. Let's suppose you've written a nice package that you think others will
find useful in their projects. How should you go about distributing it?

## Project Structure

Typically, a Python package is distributed along with other file such as a
README or installation instructions. You might have a directory structure like
the following:

{% highlight none %}
myproject
├── mypackage
│   ├── __init__.py
│   ├── one.py
│   └── two.py
└── README
{% endhighlight %}

Very commonly, when the project is a single package, `myproject` and `mypackage`
will be the same name.

It's also very common for the project directory to also be a repository of a
version control system such as git. This not only allows you to easily track
changes in the code, but when hosted on a public service such as [GitHub],
allows others to both retrieve and contribute to the source code.

## `setup.py`

In order to use your package on their system, it needs to be added to the Python
path. This is best done by the use of a setup script, distributed in the project
along with the package. The Python `setuptools` standard library module provides
functionality to do this with minimal boilerplate and in a platform-independent
way.

The following script, which would be called `setup.py` and would be placed in
the top level of the project alongside the `README` in the above example,
demonstrates how to use `setuptools` to write a minimal setup script:

{% highlight python %}
# setup.py

from setuptools import setup, find_packages

setup(
    name='myproject',
    description='A simple demonstrative project',
    packages=find_packages()
)
{% endhighlight %}

When executing this script, `setuptools` will provide all the command line
interfaces you need to build, install, package and distribute the project. For
example, to install it to your own system, run the following in the top level
directory of the project:

{% highlight bash %}
python setup.py install
{% endhighlight %}

You may need to run this command with `sudo`, or with the `--user` option, to
overcome file system permissions issues.

The `develop` option is also handy when you are continuing to work on the code;
instead of copying the package to your system packages folder, it makes links to
the source files instead, so that changes have immediate effect instead of
having to re-install after each change:

{% highlight bash %}
python setup.py develop
{% endhighlight %}

## Distribution on PyPI

The [Python Package Index (PyPI)][PyPI] is the primary repository of software
for the language, and is where most Python users get up to date packages.
Distributing a project on PyPI is quite straightforward; once you have completed
your `setup.py` (see the section on advanced features below), register your
project with PyPI with the following (you will need a PyPI account):

{% highlight bash %}
python setup.py register
{% endhighlight %}

You can then bundle and upload a source code distribution with:

{% highlight bash %}
python setup.py sdist upload
{% endhighlight %}

Be careful that everything is correct before doing the upload; it's only
possible to do the upload of a given version and distribution type once.

Once the distribution is uploaded, other users will be able to quickly and
easily install it with `pip`, the Python package manager:

{% highlight bash %}
pip install myproject
{% endhighlight %}

I recently uploaded my pyhome project, which is a dotfile management and
synchronsiation tool that I wrote a recent [blog post][pyhome] about, to PyPI.
This not only allows easier use of the tool by others, but allows me to get it
up and running quickly and easily on any new system with a single `pip install`
command.

## Advanced `setup.py` Features

`setup.py` allows you to specify a lot of extra information about your project,
which can further aid in its distribution and installation. This [example
setup.py] shows the primary fields that you should seek to complete with your
distributed project, however I would like to draw particular attention to a few
particularly useful ones:

* `version` - Specifying the version of the project (in a manner compatible with
  [PEP440]) aids with distribution and for users to track updates to the code.
* `install_requires` - When your project depends on modules not in the standard
  library, this is used by `pip` to find and install any dependencies
  automatically.
* `entry_points` and `scripts` - Commonly projects will not just be simple
  libraries, but will also provide command line utilities or other programs.
  These options tell `setup.py` how to install these to your system. `scripts`
  allows you to have a traditional Unix setup with simple executable files in a
  decidcated `bin` folder in the top level of your project, however using
  `entry_points`, while working differently, is recommended since it is more
  platform-independent. `entry_points` essentially maps a name to a function in
  a module of your project, and on installation executing that name in the shell
  will cause that function to be executed.
* `long_description` - This field is interpreted by PyPI as [reStructuredText],
  and is used to generate its project page. This can be easily done by making
  your README a [reStructuredText] document, and loading it in `setup.py`:

{% highlight python %}
# setup.py

from setuptools import setup, find_packages

with open('README.rst') as fp:
    long_description = fp.read()

setup(
    name='myproject',
    description='A simple demonstrative project',
    long_description=long_description,
    packages=find_packages()
)
{% endhighlight %}

[modpkg]: {% post_url 2016-05-08-python-modules-and-packages %}
[GitHub]: https://github.com/
[PyPI]: https://pypi.python.org/
[pyhome]: {% post_url 2016-02-10-pyhome %}
[example setup.py]: https://github.com/pypa/sampleproject/blob/master/setup.py
[PEP440]: https://www.python.org/dev/peps/pep-0440/
[reStructuredText]: http://docutils.sourceforge.net/rst.html
