---
layout: post
title:  "Neural Networks: Parallel Optimisation"
date:   2016-07-04 01:42:00 +0200
tags: machinelearning neuralnetworks python numpy scipy parallel
summary: Neural network training can be a computationally expensive task,
         especially when dealing with larger datasets. Here I document some
         optimisation of my neural network implementation to take advantage of
         the parallel performance on my computer.
series:
    name: "Neural Networks"
    index: 6
---

Training a neural network to larger data sets can be a computationally expensive
task, however if implemented in the right way we can gain substantial speedups
by leveraging parallel execution.

In my post on [parallel execution in NumPy with OpenBLAS][parallelnp], I
described how to build NumPy and SciPy to execute array operations in parallel.
In [my neural network implementation][repo], I made sure to use NumPy arrays
and array operations to perform data storage and calculation in an efficient
way. Even without the potential parallel speedups, this offers considerable
speed advantages over using native Python objects to form the data structures,
as all numerical calculations are performed using an optimised linear algebra
library.

With NumPy [built against OpenBLAS][parallelnp] and my neural network
implementation carefully leveraging NumPy array operations, my code already
performs considerably better than a naive implementation, however in this post I
describe how I squeezed a little more performance out of the code.

## Profiling

Python is often referred to as a 'batteries included' language, meaning that it
comes provided with a rich set of tools to achieve many common tasks. This is
the case for profiling, where the ``cProfile`` package of the standard library
can be easily used to comprehensively profile the execution of your code.

Wrapping the network design and training described in [Digit
Characterisation][digitchar] in the script ``train.py``, the training algorithm
was profiled by invoking Python with ``cProfile`` on the command line as
follows:

{% highlight bash %}
python -m cProfile -o train.prof train.py
{% endhighlight %}

This outputs a profile of the executation to the file ``train.prof``. Several
tools exist to visualise these profile files, however I found [SnakeViz] to work
very nicely. It is easily installed through ``pip``, the Python package manager,
and opens up an interactive graphical report in your web browser.

Using this profiling visualiser, it was quickly obvious where most of the
execution time was concentrated. As expected, a large portion of execution time
(37.3%) was in the NumPy array dot operations that perform the heavy lifting of
the algorithm, but an unexpectedly large chunk of the time (54.5%) was in the
calculation of the sigmoid function:

$$ \sigma(z) = \frac{1}{1 + e^{-z}} $$

## Optimisations

Replacing my existing implementation of the sigmoid function with a built-in
function from SciPy and removing some unneccesary repeat calculations of
$$\sigma(z)$$ gained minor improvements in execution time, however the main
reason that this code was taking so much time was that it is not run in parallel
in NumPy, unlike the dot operator (note that in the above profile I was already
using the parallel enabled NumPy [built earlier][parallelnp]).

Since NumPy does not provide the functionality to parallelise this kind of
calculation, I instead turned to the ``numexpr`` package. ``numexpr`` allows
you to define an operation in a string (e.g. ``'x + 1'``) and execute it, in
parallel, with just-in-time compilation. To enable my sigmoid calculation in
parallel, I replaced my existing NumPy implementation:

{% highlight python %}
import numpy as np
def sigmoid(z):
    return 1.0 / (1.0 + np.exp(-z))
{% endhighlight %}

with the following ``numexpr`` implementation:

{% highlight python %}
import numexpr
def sigmoid(z):
    return numexpr.evaluate('1/(1+exp(-z))')
{% endhighlight %}

Using this new code, which allows the sigmoid calculation to be performed in
parallel, the total execution time of the sigmoid function went from 512 seconds
to 86 seconds, a reduction of 83%. This also reduced the overall execution time
of ``train.py`` by 46%.

Additional modest speed improvements were gained by careful control of the
inputs to the NumPy dot operations. The underlying BLAS routine works best when
accessing contiguous blocks of memory, however the dot operation performed in
the gradient and backpropagation methods of my implementation have a transposed
array as at least one of the inputs. When a NumPy array is transposed, a new
array is not generated with a reordered copy of the data, but rather a view on
the array is generated where array accesses are mapped back onto the original
data structure. When one of the arrays is not represented by contiguous data in
memory, as in this case, the BLAS routine takes a hit in performance.

To remove this potential bottleneck, I modified my implementation to make a
contiguous copy of the data being input into the dot operation. While this did
yield an improvement in performance, the reductions in execution time were much
more modest (9% reduction in ``numpy.dot`` execution time, 6% reduction
overall).

The above optimisations were pushed to [my GitHub repository][repo] with [commit
99f69b1][optimisations].

## Scalability

Finally, I performed a scalability analysis on the training algorithm to
determine what the overall performance advantages to parallel execution were.
Training the network with the same setup for 50 iterations, using all 50,000
training examples, the number of parallel threads being used was controlled by
setting the ``OMP_NUM_THREADS`` environment variable. On my 12 core workstation,
I timed excution of the training algorithm from 1 up to 10 cores, and plotted
the execution times in the chart below:

![Parallel Scaling]({{ "/public/nn/parallel-scaling.svg" | relative_url }}){:class="centered"}

Here we can see that there is an excellent speedup up to around 4 cores, which
runs about 3 times faster than on a single core. Adding more cores after that
gains more modest speedups, with little identifiable advantage to using more
than 6 cores. It seems that even when training with the full dataset, it is
advisable to use 4 or 5 cores, which would also allow us to perform 2 training
runs simultaneously.

With these optimisations in place and with sound empirical knowledge of the
parallel performance of our training algorithm, we can now return to training
neural networks more rapidly. Check out my next posts coming soon where I'll
consider different neural network designs for the classification of handwritten
digits.

[parallelnp]: {% post_url 2016-02-08-parallel-numpy %}
[digitchar]: {% post_url 2016-06-23-digit-characterisation %}
[repo]: https://github.com/acroz/neuralnetwork
[SnakeViz]: https://jiffyclub.github.io/snakeviz/
[optimisations]: https://github.com/acroz/neuralnetwork/commit/99f69b187c3dbd076ef484bdc37fbb57c8585160#diff-09df0b76b1fedb58ae2f49e030b1418c
