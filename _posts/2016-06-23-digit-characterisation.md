---
layout: post
title:  "Digit Characterisation with Neural Networks"
date:   2016-06-23 02:32:00 +0100
categories: machinelearning neuralnetworks python numpy scipy
summary: In previous posts we covered the theory and implementation of neural
         networks. Now it's time to demonstrate a common application of them -
         recognition of handwritten digits.
series:
    name: "Neural Networks"
    index: 4
---

A common application of neural networks is pattern recognition in images. Since
we humans can effortlessly recognise shapes such as characters in text, it seems
surprising at first that programming a computer to do the same thing is so
difficult. Writing an algorithm to extract and analyse the shape of a
handwritten digit quickly becomes extremely complex as all the possible
permutations of shape and orientation, colour and intensity of the digit and its
background, etc. must be considered.

Using a neural network, on the other hand, allows us to leverage on the computer
similar processes to what is going on in our brain. The network, which knows no
specific information about the task to be performed, can be trained to a set of
inputs and outputs, with the training algorithm automatically strengthening the
right connections. The implementation and training of neural networks was
covered in detail in [the previous posts of this series](#series-posts).

In this post, I will introduce the application of neural networks to the
characterisation of handwritten digits. My neural network implementation and all
the code required to reproduce the results presented here are available [on
GitHub][repo].

## Training Data

For this application of my neural network implementation I used the excellent
[MNIST] database, which contrains a total of 70,000 images of handwritten digits
and their corresponding labels. The images and labels are provided in a
compressed binary format, for which I have provided an interpreter [in my GitHub
repository][mnist.py].

Using this tool you can easily download, read and display a random sample of the
[MNIST] images:

{% highlight bash %}
python mnist.py --download --plot --labels
{% endhighlight%}

This will look something like:

<img class="centered" src="{{ site.baseurl }}public/nn/mnist-digits.svg" />

While the [MNIST] data set comes with 60,000 training images and 10,000 test
images, we will reserve 10,000 images from the training set for
cross validation. With any machine learning algorithm, it is important to retain
a cross validation data set to compare the efficacy of different methods or
learning parameters that is independent of the test set.

## Network Setup

In the [MNIST] data set, each image is a 28x28 image of grayscale intensity
values. Since each pixel value constitues a single input feature, the first
layer of the neural network will be 784 in size. The output layer, which will
consist of one activation for each possible digit, will be 10 in size. The
number and size of the intermediate layers of the network will be a design
choice made by us.

For starters, let's consider a network with a single hidden layer of size 300,
giving a network with layers of sizes 784, 300, 10. Using [my Python neural
network code][repo], this is created as follows:

{% highlight python %}
from neuralnetwork import NeuralNetwork
categories = list(range(10)) # 0 to 9
network = NeuralNetwork([784, 300, 10])
{% endhighlight %}

## Training the Network

To train the network, the [mnist.py] module referenced above is used to first
load the training data and labels:

{% highlight python %}
import mnist
images = mnist.load_images(mnist.TRAIN_IMAGES)
labels = mnist.load_labels(mnist.TRAIN_LABELS)
{% endhighlight %}

These are then randomly shuffled and divided into training and cross validation
sets (the separate testing dataset files will be used for final testing of the
network).

{% highlight python %}
import numpy as np

# Randomly shuffle the dataset
ishuffle = np.arange(images.shape[0])
np.random.shuffle(ishuffle)
images = images[ishuffle,:,:]
labels = labels[ishuffle]

# Divide into training and cross validation examples
train_images = images[:50000,:,:]
train_labels = labels[:50000]
crossval_images = images[50000:,:,:]
crossval_labels = labels[50000:]
{% endhighlight %}

Finally, the image arrays are reshaped so that each pixel value is a single
feature:

{% highlight python %}
train_features  = train_images.reshape(50000, 784).T
crsval_features = crsval_images.reshape(10000, 784).T
{% endhighlight %}

These feature and label arrays can be used to train the neural network:

{% highlight python %}
network.train(train_features, train_labels, lmbda=5., maxiter=200)
{% endhighlight %}

and then make predictions with the ``predict`` method:

{% highlight python %}
predictions = network.predict(crossval_features)
{% endhighlight %}

## Tracking Convergence

The ``train`` method of the neural network takes an optional argument allowing
the tracking of the accuracy of the network on the cross validation dataset over
the training process. To get the ``train`` method to return the history of the
accuracy (fraction of correct predictions) of both the training and cross
validation datasets, run it as follows:

{% highlight python %}
conv = network.train(train_features, train_labels, lmbda=5.,
                     maxiter=200,
                     retaccur=(crsval_features, crsval_labels))
{% endhighlight %}

We can then plot the history of the accuracy of the iterations of the training
algorithm:

{% highlight python %}
from matplotlib import pyplot

fig = pyplot.figure()
ax = fig.add_subplot(1,1,1)

ax.plot(conv[:,0], label='Training Accuracy')
ax.plot(conv[:,1], label='CV Accuracy')

ax.set_xlabel('Iteration Count')
ax.set_ylabel('Accuracy')
pyplot.legend(loc='lower right')
{% endhighlight %}

Yielding the following:

<img class="centered" src="{{ site.baseurl }}public/nn/accuracy-evolution.svg"/>

Here we can see that the training algorithm starts with an accuracy of around
0.1, or 10%, which is what you would expect for getting the answer right by
accident 1/10 of the time with the randomly initialised parameters. The accuracy
of both the training and cross validation datasets improves rapidly, before
stabilising with a prediction accuracy above 93% after around 50 iterations.
After this, the method appears to have converged, with only modest gains in
accuracy achieved.

Importantly, the fact that we get good accuracy with the cross validation
dataset indicates that our network is not being overfitted to the training set,
and so we will have confidence that it can be applied to similar new datasets
with confidence. In later posts in this series, we will modify the network and
training algorithm to both optimise the accuracy of the network and make the
training process as efficient as possible.

[repo]: https://github.com/acroz/neuralnetwork
[MNIST]: http://yann.lecun.com/exdb/mnist/
[mnist.py]: https://github.com/acroz/neuralnetwork/blob/master/example/mnist.py
