---
layout: post
title:  "Digit Characterisation with Neural Networks: Optimisation Algorithms"
date:   2016-06-29 23:15:00 +0200
categories: machinelearning neuralnetworks python numpy scipy
summary: Selecting a good optimisation algorithm and good learning parameters is
         key to efficiently and effectively train our digit characterisation
         neural network. Here we compare several optimisers empirically.
series:
    name: "Neural Networks"
    index: 5
---

In [my last post] I introduced the application of neural networks for
handwritten digit recognition. A key part of training such a network is the
optimisation algorithm used. As explained in [Neural Network Training][nntrain],
training involves the minimisation of a cost function, which is typically
achieved through iteratively stepping in the direction of falling cost.

## Gradient Descent

One of the simplest algorithms achieving this is the gradient descent algorithm.
This algorithm uses the gradient of the cost function at the current position to
determine the direction of most rapidly decreasing cost, and takes a step in
that direction. This process is repeated until the minimum is found.

Supposing you are at some initial position $$x_n$$, and the gradient of the
cost function $$C(x)$$ is $$\nabla C(x)$$, the estimate of the minimum is
iteratively improved by the rule:

$$x_{n+1} = x_{n} - \alpha \nabla C(x_n)$$

The coefficient $$\alpha$$ is the _learning rate_ of the algorithm. With a large
$$\alpha$$, larger steps towards the minimum will be taken, meaning that the
solution may be found faster, however if the minimum is overshot there may be
oscillations or divergence, depending on the shape of the cost function. A
smaller $$\alpha$$ is safer, but may require an unreasonably large number of
iterations to find the minimum.

Which learning rate to use is application-specific, depending as stated on the
shape of the cost function being minimised. It is therefore wise to try out a
selection of learning rates, selecting the one that most quickly finds the
minimum of the cost function without oscillations.

## Application to Digit Characterisation

Using the same setup as in my last post, training of the digit characterisation
neural network is achieved using the ``train`` method:

{% highlight python %}
network.train(train_features, train_labels)
{% endhighlight %}

``train`` internally uses the [optimisation package of SciPy][spopt] to perform
the optimisation of the cost function. However, while SciPy provides a number of
more advanced optimisation algorithms, it does not provide standard gradient
descent. I have therefore provided a gradient descent algorithm [along with my
neural network code][gradientdescent.py].

To use gradient descent with ``train``, first generate the algorithm with the
desired learning rate:

{% highlight python %}
from neuralnetwork.gradientdescent import gradient_descent
alpha = 0.1
optimiser = gradient_descent(alpha)
{% endhighlight %}

Then pass it as the ``optimiser`` optional argument to ``train``:

{% highlight python %}
network.train(train_features, train_labels,
              optimiser=optimiser)
{% endhighlight %}

I performed optimisation with gradient descent with a regularisation parameter
of $$\lambda=1$$ for 50 iterations with learning rates $$\alpha$$ of 0.1, 0.2,
0.4, 0.6 and 1.0. The graph below shows how the cost function for each learning
rate converged over time:

![Learning Rate]({{ "/public/nn/learning-rate.svg" | relative_url }}){:class="centered"}

Looking at this chart, we see that the largest learning rate of $$\alpha=1.0$$
resulted in a lot of oscillations and slow convergence. The smallest learning
rate of $$\alpha=0.1$$ was better, but also had slower convergence than some of
the intermediate values. I selected $$\alpha=0.4$$ as the best learning rate
here, as it converged quickly without oscillations.

## Comparison with other Optimisers

Using the [SciPy optimisation package][spopt] as the framework for our
optimisation process was not accidental. While it does not supply standard
gradient descent as an optimiser, it does provide a number of other, more
advanced optimisers that could be used in training our neural network.

In particular, the _Conjugate Gradient_ and _Newton-CG_ optimisers are relevant
to our problem. They are both unconstrained, take advantage of our efficient
method for calculation of the cost function gradient, but do not require
calculation of the second derivatives. Using the same setup as with the gradient
descent training above, I trained using these algorithms for 50 iterations with
a regularisation parameter of $$\lambda=1$$. The graph below shows the evolution
of the cost using each of these methods and with gradient descent with the
optimal learning rate discovered above.

![Comparison of Optimisers]({{ "/public/nn/compare-optimisers.svg" | relative_url }}){:class="centered"}

Here we can see that the Conjugate Gradient method results in significantly
better convergence than either the gradient descent or Newton-CG methods.
Usefully, these methods also do not require a choice of learning rate.

The implementation of the Conjugate Gradient optimiser is beyond the scope of
this blog post, but we have discovered that it offers significant improvements
over standard gradient descent when training our neural network to recognise
handwritten digits. In future posts we will look at choice of regularisation
parameter and network design with the goal of further improving the accuracy of
our digit classifier.

[my last post]: {% post_url 2016-06-23-digit-characterisation %}
[nntrain]: {% post_url 2016-02-17-neural-network-training %}
[spopt]: http://docs.scipy.org/doc/scipy-0.17.0/reference/optimize.html
[gradientdescent.py]: https://github.com/acroz/neuralnetwork/blob/master/neuralnetwork/gradientdescent.py
