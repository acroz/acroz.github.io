---
layout: post
title:  "Neural Network Training"
date:   2016-02-17 20:01:00 +0100
categories: machinelearning neuralnetworks python numpy scipy
summary: Neural networks are a powerful technique in machine learning, inspired
         by models of the brain. In this post, I show how to train a network to
         some data.
series:
    name: "Neural Networks"
    index: 3
---

In [this series of posts](#series-posts), I have already shown the basic idea
behind computational neural networks as a machine learning technique and the
implementation of the forward propagation algorithm. In this post, we will now
look into a method for fitting such a network to a set of training data.

## Cost Function

The direct outputs from a neural network are, as discussed in [previous posts
](#series-posts), the activations of the output layer. Each entry of the output
activations corresponds to a specific classification predicted by the network,
with values ranging from 0 to 1. The closer these activations are to 1, the
more likely the network thinks that classification is for the network inputs
provided.

In the 'ideal' case, the output activations for a network with 4 outputs and
for input data corresponding to a class of 3 would be:

$$ \mathbf{a}^{(L)} = \left[ \begin{matrix}0\\0\\1\\0\end{matrix} \right] $$

Say that, in reality, the network predicted output activations of:

$$ \mathbf{a}^{(L)} = \left[
    \begin{matrix}0.12\\0.02\\0.87\\0.26\end{matrix}
\right] $$

This would give the correct prediction, but as the entry for output 3 becomes
smaller and the others become larger, the prediction is less and less
'certain'. The closer the output activation is to the ideal case above, the
better our confidence in its prediction, and so we would want the trained
network to minimise the difference between the ideal output activations, which
we will denote from here on as $$\mathbf{y}$$, and the actual ones
$$\mathbf{a}^{(L)}$$.

A popular choice of cost function for such a situation would be the mean
squared error:

$$
    \left\| \, \mathbf{y} - \mathbf{a}^{(L)} \right\|^2 
        = \sum_j \left( y_j - a_j^{(L)} \right)^2
$$

However, for neural networks a better cost function to use for training turns
out to be the cross entropy cost function:

$$
    - \left[
        \mathbf{y} \cdot \ln \mathbf{a}^{(L)} 
        + (1 - \mathbf{y}) \cdot \ln (1 - \mathbf{a}^{(L)})
    \right] \\
    = - \sum_j \left[
        y_j \ln a_j^{(L)} + (1 - y_j) \ln (1 - a_j^{(L)})
    \right]
$$

The reasons why this cost function are better are beyond the scope of this post
series, however for further reading on the topic I refer you to [Michael
Nielsen's excellent guide on neural networks][nielsen-crossentropy].

As we usually wish to evaluate the cost of the network given a set of training
examples, this can be extended to:

$$
    - \frac{1}{n} \sum_{i=1}^n \left[
        \mathbf{y}_i \cdot \ln \mathbf{a}_i^{(L)} 
        + (1 - \mathbf{y}_i) \cdot \ln (1 - \mathbf{a}_i^{(L)})
    \right]
$$

where we average the cost over all provided training examples.

### Regularisation

To prevent overfitting, an additional regularisation term is added to the cost
function:

$$ \frac{\lambda}{2n} \sum_{l=1}^L \left\| \, \mathbf{w}^{(l)} \right\|^2 $$

where the coefficient $$\lambda > 0$$ is the regularisation parameter. Simply
speaking, this term in the cost function penalises larger weights on the
neurons, effectively preventing the network from forming more complex
hypotheses than are apropriate. Choosing $$\lambda$$ requires some empirical
study of the specific application, and will be discussed in a later post of the
series.

### Implementation

Calculation of the above cost function is implemented by the `cost` method of
the `NeuralNetwork` class in [my project repository][repo]. See below how this
method propagates the activations through the network, calculates the cross
entropy cost as above and then adds on the regularisation penalty:

{% highlight python %}
import numpy as np
class NeuralNetwork(object):
    ...
    def cost(self, features, outputs, lmbda=0.0, ...):
        
        # Get once
        n_examples = features.shape[1]

        # Propagate activations through network, storing the results
        a = features
        results = []
        for layer in self._layers:
            res = layer.forward(a)
            results.append(res)
            a = res.a
        
        # Evaluate the cross entropy cost function
        components = - (outputs * np.log(a)) \
                     - (1 - outputs) * np.log(1 - a)
        cost = components.sum() / n_examples

        # Regularisation
        if lmbda > 0:
            scale = lmbda / (2 * n_examples)
            for layer in self._layers:
                cost += scale * layer.regularisation_penalty()
       
        return cost
{% endhighlight %}

The regularisation cost is calculated using the `regularisation_penalty` method
of the `NeuralNetworkLayer` class, which simply returns the summed squared 
weights for that layer:

{% highlight python %}
class NeuralNetworkLayer(object):
    ...
    def regularisation_penalty(self):
        return (self._weights**2).sum()
{% endhighlight %}

## Cost Function Gradient

We have code to compute the cost function for a particular neural network, but
how do you go about finding the configuration of the network that minimises
this cost function, and thus has the best predictive power?

This is an optimisation problem. There are a number of ways to approach it,
such as with a parameter sweep (try many different networks with different
parameters (weights and biases) and see which works best), however with a well
behaved cost function with a large number of parameters a gradient descent
method works well.

Explaining the detail behind gradient descent is beyond the scope of this
series of posts, but in essence it is like finding the lowest point in a bowl.
Considering height of the point in the bowl as cost, we can find the bottom by
moving in the direction of greatest descending steepness. Proceeding step-wise
in such a fashion, one can arrivive at the minumum cost/height.

The gradient of a cost function $$C(\mathbf{x})$$ can be calculated by a finite
differencing approach:

$$ 
    \frac{\partial C}{\partial x_i} 
        \approx \frac{C(x_i + \Delta x) - C(x_i)}{\Delta x}
$$

However for a model with as many parameters as a neural network, estimating the
partial derivatives for all parameters in this way will be very slow.

### Backpropagation Algorithm

Instead, we use a neural network-specific method for calculating the gradient.
In the backpropagation algorithm, we first estimate the errors on all neurons
of the network, then use another relation to calclulate the gradient of the
cost function with respect to each weight and bias.

This is done with the following relations. Firstly, the error of a neuron is
defined as:

$$ \delta_j^{(l)} \equiv \frac{\partial C}{\partial z_i^{(l)}} $$

It can be shown that for the cross entropy cost function, the error in the
output layer $$l=L$$ can be simply calculated with:

$$ \delta_j^{(L)} = a_j^{(L)} - y_j $$

or in vector notation:

$$
    \mathbf{\unicode{x3b4}}^{(L)} = \mathbf{a}^{(L)} - \mathbf{y}
    \label{deltalast}\tag{1}
$$

These errors can be propagated back through the network using the relation:

$$
    \mathbf{\unicode{x3b4}}^{(l)} 
        = \left(
            \left( \mathbf{w}^{(l+1)} \right)^T
            \mathbf{\unicode{x3b4}}^{(l+1)}
          \right)
        \odot \sigma'\left( \mathbf{z}^{(l)} \right)
    \label{backprop}\tag{2}
$$

where $$\odot$$ is the Hadamard, or element-wise, product and $$\sigma'$$ is
the first derivative of the sigmoid function.

The gradient of the cost function with respect to a single weight is then given
by:

$$ 
    \frac{\partial C}{\partial w_{jk}^{(l)}}
        = a_k^{(l-1)} \delta_j^{(l)} + \lambda w
    \label{gradweight}\tag{3}
$$

and with respect to a single bias is:

$$
    \frac{\partial C}{\partial b_j^{(l)}} = \delta_j^{(l)}
    \label{gradbias}\tag{4}
$$

For additional insights into the backpropagation algorithm and information on
the derivation of the above equations, please see [the backpropagation chapter
][nielsen-backprop] of Michael Neilsen's online book on neural networks.

### Implementation

Equations $$\ref{deltalast}$$ to $$\ref{gradbias}$$ above are implemented in my
[neural network project][repo] once again through interaction of the
`NeuralNetwork` and `NeuralNetworkLayer` classes. The gradient is computed
within the `cost` method of the `NeuralNetwork` class when the `gradient`
optional argument is set to `True`:

{% highlight python %}
class NeuralNetwork(object):
    ...
    def cost(self, features, outputs, lmbda=0.0, gradient=False):
        
        # Get once
        n_examples = features.shape[1]

        # Propagate activations through network, storing the results
        a = features
        results = []
        for layer in self._layers:
            res = layer.forward(a)
            results.append(res)
            a = res.a
        
        # Cost computed as in snippet above
        ...
       
        # Don't compute gradient if not requested
        if not gradient:
            return cost
        
        # Use backwards propagation algorithm to compute gradients
        # Compute errors in final layer
        delta = a - outputs

        gradient_parts = []
        
        # Loop backwards over layers and results
        for layer, res, res_prev in zip(self._layers[::-1],
                                        results[::-1][:-1],
                                        results[::-1][1:]):
            
            # Compute and store gradients for this layer
            grad = layer.gradient(delta, res.x, lmbda)
            gradient_parts.append(grad)
            
            # Backpropagate errors
            delta = layer.backward(delta, res_prev.z)
        
        # Compute and store gradients for first layer
        grad = self._layers[0].gradient(delta, results[0].x, lmbda)
        gradient_parts.append(grad)

        # Stick gradients together in forward order
        gradient_flat = np.concatenate(gradient_parts[::-1])

        return cost, gradient_flat
{% endhighlight %}

Here, the line:

{% highlight python %}
delta = a - outputs
{% endhighlight %}

corresponds to equation $$\ref{deltalast}$$, computing the errors in the output
layer. The errors are then propagated backwards inside the loop using the
`backward` method of the `NeuralNetworkLayer` class, which implements equation
$$\ref{backprop}$$:

{% highlight python %}
def sigmoid_prime(z):
    return sigmoid(z) * (1 - sigmoid(z))

class NeuralNetworkLayer(object):
    ...
    def backward(self, delta, z_layerm1):
        # Compute the deltas of the input layer using its provided
        # augmented inputs and this layer's deltas
        return np.dot(self._weights.T, delta) \
               * sigmoid_prime(z_layerm1)
{% endhighlight %}

Equations $$\ref{gradweight}$$ and $$\ref{gradbias}$$ are implemented by the
`gradient` method of `NeuralNetworkLayer`:

{% highlight python %}
import numpy as np
class NeuralNetworkLayer(object):
    ...
    def gradient(self, delta, a_input, lmbda=0.0):

        # Get the number of samples from second axis of array
        n_samples = a_input.shape[1]

        # Compute the gradient of the cost function wrt the weights,
        # averaged over all the given samples
        grad_weights = np.dot(delta, a_input.T) / n_samples

        # Add on the gradient of the regularisation term
        if lmbda > 0.0:
            grad_weights += (lmbda/n_samples) * self._weights

        # Compute the gradient of the cost function wrt the biases,
        # averaged over all the given samples
        grad_biases = np.sum(delta, axis=1) / n_samples

        # Return a 1D array of the gradients in the same order as
        # the parameters property
        return np.concatenate((grad_weights.ravel(),
                               grad_biases.ravel()))
{% endhighlight %}

Note that this method returns the gradients in the same order as parameters
for that layer are set. The `cost` method of `NeuralNetwork` computes and 
stores the gradients for each layer as it moves backwards through the network,
finally assembling the gradients for the whole network and returning them along
with the cost:

{% highlight python %}
# Stick gradients together in forward order
gradient_flat = np.concatenate(gradient_parts[::-1])
return cost, gradient_flat
{% endhighlight %}

## Training

With the functionality in place to compute the cost and its gradient, it is
possible to begin training the network to some data! In [this project][repo], I
used the ready made optimisation algorithms from [SciPy]. The `training` method
of the `NeuralNetwork` class combines these algorithms with the cost and
gradient functionality to train a network to some provided data:

{% highlight python %}
from scipy.optimize import minimize
class NeuralNetworkLayer(object):
    ...
    def train(self, features, labels, lmbda=0.0, optimiser='CG',
              maxiter=None):

        # Store a list of unique categories
        self._mapper.register(labels)

        # Evaluate a matrix of output activations for training
        activations = self._mapper.activations(labels)
        
        # Randomly initialise the parameters of the network
        self.initialize_parameters()

        # Cost function for optimiser
        def cost(params):
            # Modify the parameters
            self.parameters = params
            # Return the new cost
            return self.cost(features, activations, lmbda,
                             gradient=True)
        
        # Train the network
        result = minimize(cost, self.parameters, method=optimiser,
                          jac=True, options={'maxiter': maxiter})
        
        # Set network parameters to optimal values
        self.parameters = result.x
{% endhighlight %}

Provided the input features/activations and output labels for a set of training
examples, this method maps the labels to output activations, then wraps the
network's cost function before passing it to the `minimize` optimisater
interface. [SciPy] then calls the wrapped cost function as needed to find the
optimal parameter set.

### Improving Training Speed

In order to take full advantage of its efficient C backend, all significant
number crunching in this implementation is done using [NumPy] array operations.
These arrays use the efficient [BLAS] linear algebra library to perform
calculations quickly.

To further improve performance when training to larger data sets, I recommend
ensuring that your NumPy installation is [compiled to execute in parallel
][parallel-numpy], taking advantage of modern multi-core systems. This is
particularly effective on my workstation, which has 12 physical CPUs.

[nielsen-backprop]: http://neuralnetworksanddeeplearning.com/chap2.htmln
[nielsen-crossentropy]: http://neuralnetworksanddeeplearning.com/chap3.html#the_cross-entropy_cost_function
[repo]:  https://github.com/acroz/neuralnetwork
[NumPy]: http://www.numpy.org/
[SciPy]: http://www.scipy.org/
[BLAS]:  http://www.netlib.org/blas/
[parallel-numpy]: {% post_url 2016-02-08-parallel-numpy %}
