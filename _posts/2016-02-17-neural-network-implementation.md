---
layout: post
title:  "Neural Network Implementation"
date:   2016-02-17 12:08:00 +0100
tags: machinelearning neuralnetworks python numpy scipy
summary: Neural networks are a powerful technique in machine learning, inspired
         by models of the brain. In this post, we expand on the implementation
         of practical neural networks.
series:
    name: "Neural Networks"
    index: 2
---

In the [first post of this series][post1], I introduced the basic concept of
neural networks and wrote down the relation for a single neuron. Here, I
provide more detail on the mathematics and implementation of a complete
network.

## Nomenclature

As in the case of the single neuron, $$\{x_i\}$$ denotes inputs to a neuron,
$$a$$ represents its activation (output), and $$\{w_i\}$$ and $$b$$ refer to
weights and bias respectively. We also introduce here the "augmented input"
$$z$$, corresponding to the input to the activation function $$g$$. In summary:

$$ z = \sum_i w_i x_i + b $$

$$ a = g \left( z \right) $$

As we will always use the sigmoid function $$\sigma(x)$$ as the activation
function here, from now on we will refer to them directly, though it is
possible to use other activation functions:

$$ g(t) = \sigma(t) = \frac{1}{1 + e^{-t}} $$

In a network with multiple layers and multiple neurons per layer, we also need
to introduce additional indices to refer to the relevant properties of
individual neurons. Consider once again the example network shown in the [first
post of this series][post1], now with the layers of the network numbered from 1
to 3:

![Simple Network with Highlights]({{ "/public/nn/network-highlights.svg" | relative_url }}){:class="centered"}

The values referring to a particular neuron are now referred to using a
superscript index $$l$$ to refer to the network layer, and subscript indices
$$j$$ and $$k$$ to refer to the $$j$$th neuron of a particular layer and the
$$k$$th input to that neuron.

In the above network, the highlighted neuron is number $$j=2$$ of layer
$$l=2$$, so its activation, highlighted in blue, is given by $$a_2^{(2)}$$, and
its input from neuron $$k=2$$ of layer $$l-1$$, highlighted in orange, is given
by $$x_{22}^{(2)}$$. Similarly, the weight corresponding to input
$$x_{22}^{(2)}$$ is denoted by $$w_{22}^{(2)}$$, and the bias of the
highlighted neuron is $$b_2^{(2)}$$.

Introducing these notations to the above relations for a single neuron, we
have:

$$ z_j^{(l)} = \sum_k w_{jk}^{(l)} x_{jk}^{(l)} + b_j^{(l)} $$

$$ a_j^{(l)} = \sigma \left( z_j^{(l)} \right) $$

## Vectorisation

Writing out the above indices can be time consuming, so it is usually
convenient to write out the parameters and values mentioned above as vectors.
All of the activations of a particular layer $$l$$, $$\{z_j^{(l)}\}$$, for
example, can be written together as $$\mathbf{z}_j$$. The equations for a
single neuron then become:

$$ z_j^{(l)} = \mathbf{w}_j^{(l)} \cdot \mathbf{x}_j^{(l)} + b_j^{(l)} $$

or further:

$$ \mathbf{z}^{(l)} = \mathbf{w}^{(l)} \cdot \mathbf{x}^{(l)} + \mathbf{b}^{(l)} $$

and

$$ \mathbf{a}^{(l)} = \sigma \left( \mathbf{z}^{(l)} \right) $$

In addition, since $$x_{jk}^{(l)} = a_k^{(l-1)}$$ we can write the relation:

$$ \mathbf{z}^{(l)} = \mathbf{w}^{(l)} \cdot \mathbf{a}^{(l-1)} + \mathbf{b}^{(l)} $$

Starting with input activations $$\mathbf{a}^{(0)}$$, we can propagate the
activations through the network using the above relations for $$\mathbf{z}$$
and $$\mathbf{a}$$, and so arrive at the output activations.

## Making Predictions

When using a neural network, the output layer provides a set of activation
values $$\{a_j^{(l)}\}$$. To use the network to perform a classification
problem, each of these activations is assigned to a particular class, and the
activations are considered as something analagous to the probability of the
input being of that class. The class predicted by the network can then be
determined by:

$$ \mathop{\mathrm{argmax}}\limits_j a_j^{(L)} $$

where $$l=L$$ is the last layer of the network.

## Implementation

The above forward propagation and prediction methods are implemented in my
neural network Python project, [available on GitHub][repo]. The implementation
there is divided into two main classes, `NeuralNetwork` and
`NeuralNetworkLayer`, which store their parameters and perform processing using
[NumPy arrays][NumPy].

These classes work together to perform the forward propagation of input
activations to outputs. The `NeuralNetworkLayer` performs the propagation for a
single layer:

{% highlight python %}
import numpy as np

def sigmoid(z):
    return 1.0 / (1.0 + np.exp(-z))

class NeuralNetworkLayer(object):
    ...
    def forward(self, x)

        # Compute augmented inputs
        z = np.dot(self._weights, x) + self._biases[:,np.newaxis]

        # Compute activations
        a = sigmoid(z)

        # Return the result
        return LayerResult(x, z, a)
{% endhighlight %}

The `NeuralNetwork` class passes activations through successive layers to
process the whole network:

{% highlight python %}
class NeuralNetwork(object):
    ...
    def forward(self, input_activations):

        # For compactness
        a = input_activations

        # Propagate through the network layers
        # Each layer is an instance of NeuralNetworkLayer
        for layer in self._layers:
            a = layer.forward(a).a

        # Return the result
        return a
{% endhighlight %}

Predictions can be readily done using the `predict` method, which takes input
activations and automatically maps the forward-propagated output activations
to the appropriate category labels.

[post1]: {% post_url 2016-02-16-neural-networks %}
[repo]:  https://github.com/acroz/neuralnetwork
[NumPy]: http://www.numpy.org/
