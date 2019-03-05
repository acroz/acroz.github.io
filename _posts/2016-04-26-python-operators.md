---
layout: post
title:  "Customising Operators in Python"
date:   2016-04-24 22:44:00 +0100
tags: [Python]
summary: Python classes allow powerful encapsulation and abstraction of code,
         but even more elegant code can be achieved through the application of
         operators to classes.
---

Python classes allow the encapsulation of functionality in cleanly defined
objects, and when used well can allow abstractions in usage that make for more
understandable and readable code.

Consider the simple example of a class that defines a 3-vector, which I will
call `Vector3`. It takes an x, y and z value and implements simple addition of
other vectors:

{% highlight python %}
class Vector3(object):
    """
    Describes a 3-vector.
    """

    def __init__(self, x, y, z):
        self.x = float(x)
        self.y = float(y)
        self.z = float(z)

    def add(self, other):
        """
        Compute the sum of this and another vector.
        """

        # Sum the coordinates
        x = self.x + other.x
        y = self.y + other.y
        z = self.z + other.z
        
        # Create the new vector and return
        return Vector3(x, y, z)
{% endhighlight %}

In code which manipulates vectors, we no longer need to manually write out the
addition operations for each of the coordinates, but can simply add two vectors
like:

{% highlight python %}
vec1 = Vector3(1, 2, 2)
vec2 = Vector3(2, 1, 0)
newvec = vec1.add(vec2)
{% endhighlight %}

## Defining Operators

The `add` method above is a nice abstraction, however it is limited by the fact
that we need to know to remember the interface, and that the use of a method
call with the second object as an argument is a little clunky. A nice solution
is to make our class support the `+` addition operator, so that the last line
of the above code snippet becomes simply:

{% highlight python %}
newvec = vec1 + vec2
{% endhighlight %}

Python achieves this through the use of special methods, identifiable by
starting and ending with two underscores. You may have seen other special
methods like `__init__` above, however some of these methods define the
behaviour when an operator is applied.

By default, trying to add two objects of a cusom class will result in a
`TypeError`:

{% highlight python %}
vec1 + vec2
# TypeError: unsupported operand type(s) for +: 'Vector3' and 'Vector3'
{% endhighlight %}

To support the addition operator, we need to define the
`__add__` method with the signature:

{% highlight python %}
def __add__(self, other):
{% endhighlight %}

Fortunately, this has the same signature as the `add` method we defined above,
so simply renaming the method to `__add__` will make additions of `Vector3`
objects work as intended.

## Complete Implementation

Any of the Python operators can be overloaded in this way - see the
documentation on the [Python data model] for a full listing, but the most
commonly used are the numeric operators:

* `+` -- `__add__`
* `-` -- `__sub__`
* `*` -- `__mul__`
* `/` -- `__truediv__`
* `**` -- `__pow__`

and the logical operators:

* `==` -- `__eq__`
* `!=` -- `__ne__`
* `<` -- `__lt__`
* `>` -- `__gt__`
* `<=` -- `__le__`
* `>=` -- `__ge__`
* `and` -- `__and__`
* `or` -- `__or__`

There are also the augmented assignment operators, that modify a variable
in-place, usually used for scaling or incrementing numeric values. These are
named with a leading 'i', like `__iadd__` for the `+=` operator.

Below is a more complete version of the `Vector3` class from above,
demonstrating the implementation and usage of the normal and in-place additon
and subtraction operators. A `__str__` special method has also been added to
provide decriptive printing of `Vector3` objects when passed to the `print`
function.

{% highlight python %}
class Vector3(object):
    """
    Describes a 3-vector.
    """

    def __init__(self, x, y, z):
        self.x = float(x)
        self.y = float(y)
        self.z = float(z)

    def __str__(self):
        """
        Return a formatted string representation of the vector.
        """
        return 'Vector3({}, {}, {})'.format(self.x, self.y, self.z)

    def __add__(self, other):
        """
        Compute the sum of this and another vector.
        """

        # Sum the coordinates
        x = self.x + other.x
        y = self.y + other.y
        z = self.z + other.z
        
        # Create the new vector and return
        return Vector3(x, y, z)

    def __sub__(self, other):
        """
        Compute the difference of this and another vector.
        """

        # Subtract the coordinates
        x = self.x - other.x
        y = self.y - other.y
        z = self.z - other.z
        
        # Create the new vector and return
        return Vector3(x, y, z)

    def __iadd__(self, other):
        """
        Add on another vector in-place.
        """

        self.x += other.x
        self.y += other.y
        self.z += other.z

        return self

    def __isub__(self, other):
        """
        Subtract another vector in-place.
        """

        self.x -= other.x
        self.y -= other.y
        self.z -= other.z

        return self

# Example Usage

# Define two initial vectors
vec1 = Vector3(1, 0, 0)
vec2 = Vector3(0, 1, 0)

# Add and print
print(vec1 + vec2)
# Vector3(1.0, 1.0, 0.0)

# Subtract and print
print(vec1 - vec2)
# Vector3(1.0, -1.0, 0.0)

# Add in-place
vec1 += vec2
print(vec1)
# Vector3(1.0, 1.0, 0.0)

# Subtract a new vector in-place
vec1 -= Vector3(0, 0, 1)
print(vec1)
# Vector3(1.0, 1.0, -1.0)
{% endhighlight %}

[Python data model]: https://docs.python.org/2/reference/datamodel.html
