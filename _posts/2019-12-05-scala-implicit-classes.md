---
layout: post
title:  "Implicit Classes in Scala"
date:   2019-12-05 22:39:00 +0000
tags:   [Scala]
---

Scala [implicit classes] allow you to augment the behaviour of existing objects
with new functionality. This pattern, sometimes called _"Pimp my library"_,
provides a useful method to implement expressive Scala code.

## Syntax

To create an implicit class, add the `implicit` keyword before the class
definition. Note that implicit classes have to be constructed inside other
traits, classes or objects:

```scala
object Implicits {
  implicit class DoubleListOps(values: List[Double]) {
    def mean: Double = values.sum / values.length
  }
}
```

When this implicit class is in scope, the methods it defines will can be called
as if they were methods on values of the type it wraps. For example, in the
example above, we can now call `.mean` on any `List[Float]`:

```scala
scala> import Implicits._
import Implicits._

scala> val numbers = List(10.2, 12.1, 11.6)
numbers: List[Double] = List(10.2, 12.1, 11.6)

scala> numbers.mean
res0: Double = 11.299999999999999
```

Implicit classes only work with one normal argument, but can take additional
implicit arguments. For example, we can make the above 'mean' functionality
generic to all numeric types:

```scala
object Implicits {
  implicit class NumericListOps[A](values: List[A])(
    implicit num: Numeric[A]
  ) {
    def mean: Double = num.toDouble(values.sum) / values.length
  }
}
```

This can be used with any number type, for example with `Int`s:

```scala
scala> import Implicits._
import Implicits._

scala> List(1, 2, 3).mean
res0: Double = 2.0
```

## Notes

This pattern is sometimes called _"Pimp my library"_ as it allows you to extend
the functionality of objects implemented in libraries you have no control over!
In fact, this is very similar to how Scala extends the `String` type from Java
with additional functionality.

I hope you have seen that implicit classes provide a useful tool for writing
expressive and concise code in Scala. For more information, have a look at the
[scala docs][implicit classes].

[implicit classes]: https://docs.scala-lang.org/overviews/core/implicit-classes.html
