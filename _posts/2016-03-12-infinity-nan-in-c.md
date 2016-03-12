---
layout: post
title:  "Infinities and NaN in C"
date:   2016-03-12 16:59:00 +0100
categories: c float
summary: Some mathematical operations can result in infinities or have
         undefined results. Fortunately, C can return sensible results in these
         cases through special floating point values representing
         positive/negative infinities and "not a number".
---

A common application of programming languages such as C is to perform numerical
calculations, however some mathematical operations which are possible to
perform have infinite or undefined results. For example, $$1/0$$ results in a
positive infinity, $$\log(0)$$ results in a negative infinity and $$\sqrt{-1}$$
is undefined for real numbers.

Fortunately, C provides a sensible way of storing and returning the result of
such operations - it does not simply crash the program. This allows us to
handle such outcomes senbily in our program. Returned infinite results are
called just that, whereas undefined results are called "not a number", or NaN.

## Storage

Infinities and NaNs are stored in a unique way in the floating point data
structure that does not conflict with other possible values.

Floating point numbers are stored as three integers - a sign bit $$s$$, a
coefficient $$c$$, and an exponent $$q$$. The value of a decimal number is then
given by:

$$ (-1)^s \times c \times 10^q $$

For example, the number 10.3452 would be represented as $$s=0$$, $$c=103452$$,
$$e=-4$$, giving:

$$ (-1)^0 \times 103452 \times 10^{-4} = 10.34524 $$

The special values of infinity and NaN are represented by filling the exponent
field bits with 1s. Positive and negative infinity have the coefficient part
equal to zero, while the sign bit indicates the sign of the infinity. NaNs have
the same exponent part, but have the coefficient as non-zero. The storage and
behaviour of these values is set out in [IEEE standard 754][IEEE 754].

## Logical Tests

An interesting feature of NaN is that, by design, it is _unordered_, meaning
that it is not equal to, less than or greater than any value, including itself.
All of these statements will be false when x is NaN:

{% highlight c %}
x == x; // false
x < x;  // false
x > x;  // false
{% endhighlight %}

This provides a possible way to test for a NaN in code - it is the only float
for which `x == x` will be false. However, it is recommended to instead use the
[macros defined in `math.h`][GNU special]. These include `NAN` and `INFINITY`,
macros defining these values as constants, and the `isfinite` and `isnan`
macros, which allow testing for values of these types:

{% highlight c %}
#include <math.h>
isnan(NAN);         // true
isfinite(INFINITY); // false
isfinite(NAN);      // false
1./0. == INFINITY;  // true
{% endhighlight %}

These special values offer an efficient way of storing and handling the
infinite or undefined results of numerical computations. Programs which may
accidentally perform such calculations can continue on regardless and at least
partially complete their task, providing possibly useful results but also
allowing better analysis of the code and why it failed.

[IEEE 754]: https://en.wikipedia.org/wiki/IEEE_floating_point
[GNU special]: http://www.gnu.org/software/libc/manual/html_node/Infinity-and-NaN.html
