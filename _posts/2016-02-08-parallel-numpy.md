---
layout: post
title:  "Parallel NumPy with OpenBLAS"
date:   2016-02-08 22:25:00 +0100
tags: python numpy parallel arch
summary: Distributions of NumPy from the package manager often fail to take
         advantage of the computational power available on a multicore system.
         Follow these steps to enable parallel computations with OpenBLAS.
---

[NumPy] is a fantastic resource for doing numerical computations in Python,
allowing significant speedups by allowing efficient C-implemented operations in
the back end do the heavy lifting. However, standard shipped [NumPy]
implementations from Linux package systems and through [pip] do not take
advantage of the potential speed improvments available by executing appropriate
array operations in parallel.

In order to do such operations in parallel, we must build it against a
supported parallel implementation of BLAS/LAPACK, which are the libraries used
to perform linear algebra in NumPy. Some of the supported implementations can
be challenging to build themselves, however I found success with [OpenBLAS].

## NumPy

Having installed [OpenBLAS] using the ``openblas-lapack`` package from the
[Arch Linux User Repository][AUR], I downloaded the latest version of NumPy
from github and created a new build config from the template:

{% highlight bash %}
git clone git://github.com/numpy/numpy.git
cd numpy
cp site.cfg.example site.cfg
{% endhighlight %}

I then uncommented the [OpenBLAS] section and changed the paths to the correct
ones for my system (``pacman -Ql openblas-lapack`` was of use to locate these
paths on my Arch Linux system) and built and installed [NumPy] with:

{% highlight bash %}
python setup.py build
sudo python setup.py install
{% endhighlight %}

Opening an interactive Python shell, I was able to verify that the operations
were running in parallel by executing the following instructions and observing
CPU usage in ``htop``:

{% highlight python %}
import numpy as np
a = np.random.rand(10000, 10000)
b = np.random.rand(10000, 10000)
np.dot(a, b)
{% endhighlight %}

## SciPy

The [SciPy] package, an additional set of scientific tools built around
[NumPy], is compiled in much the same way. First, ensure that Cython is
installed and retrieve the [SciPy] sources:

{% highlight bash %}
sudo pip install Cython
git clone git://github.com/scipy/scipy.git
{% endhighlight %}

Then make a config file from the template, uncomment and update the [OpenBLAS]
entries, build and install just as with [NumPy].

[NumPy]: http://www.numpy.org/
[SciPy]: http://www.scipy.org/
[pip]: https://pypi.python.org/pypi/pip
[OpenBLAS]: http://www.openblas.net/
[AUR]: https://aur.archlinux.org/
