---
layout: post
title:  "Neural Networks"
date:   2016-02-16 18:33:00 +0100
tags: machinelearning neuralnetworks python numpy scipy
summary: Choosing a suitable mathematical model for your machine learning
         problem can be challenging. Neural networks provide a
         neurology-inspired method with minimal prior assumptions and great
         predictive power.
series:
    name: "Neural Networks"
    index: 1
---

Devising a mathematical model of a system requires careful thought so that it
accurately represents the system. In relatively simple applications, for
example in calculating the trajectory of a ball launched with a certain
velocity, the underlying physics can be represented directly by the model. In
such an example, the equations of Newtonian mechanics can be integrated to
calculate the path of the ball.

As the underlying system becomes more complex, for example when modelling a
biological system, simplifications and approximations must be made, as the
system becomes too large to model explicitly.

In machine learning, the physics or relationships underlying the data may not
be known at all - in fact, it is usually our goal to discover these
relationships through our analysis of the data with no or limited _a priori_
knowledge. Deciding on a suitable mathematical model to fit to the available
data can then be a difficult task - the choice of an unsuitable model may
unfairly bias the results of the analysis.

## Inspiration from Neurology

Originally devised to model and study the mechanisms of the brain,
computational neural networks have increasingly found utility as a powerful
machine learning technique. The brain is modelled as a large network of
neurons, each of which is considered to be a simple computational unit taking
a number of inputs $$\{x_i\}$$ and providing a single output (or "activation")
$$a$$. The activation is calculated by applying weights $$\{w_i\}$$ and a bias
term $$b$$ and passing to an activation function $$g$$:

$$ a = g \left( \sum_i w_i x_i + b \right) $$

A common choice for \\(g\\) is the sigmoid function:

$$ g(x) = \sigma(x) = \frac{1}{1 + e^{-x}} $$

Neurons are often depicted as below, receiving a number of inputs from the left
and providing an output to the right:

![Single Neuron]({{ "/public/nn/single-neuron.svg" | relative_url }}){:class="centered"}

A more complex model can then be constructed by assembling a network of such
neurons, where multiple layers of neurons have their inputs and outputs
connected together:

![Simple Network]({{ "/public/nn/simple-network.svg" | relative_url }}){:class="centered"}

More complex structures with reentrant positive feedback loops are also
possible and may offer additional power, however here we concentrate on the
simpler unidirectional, layer-arranged structure as above. Note that while some
neurons in the above network appear to provide different outputs, the different
arrows leaving a neuron in fact correspond to the same output being sent to
multiple neurons in the next layer of the network.

## Intuition

By combining together a network of simple computational networks, it is
possible to form a network capable of producing a wide range of mathematical
representations. A set of inputs $$\{x_i\}$$ can be provided to the input
layer, processed through the neural network, and a useful output or outputs
$$\{a_i\}$$ then generated. This is how real neural networks in the brain are
thought to work, and the application of the concept to machine learning turns
out to be a powerful technique.

## Further Detail

For further detail on the implementation and application of neural networks to
a handwritten digit recognition system, see the [list of other posts in this
series below](#series-posts).
