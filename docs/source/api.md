# API

## Regular CD diagrams

A regular CD diagram with ``n`` observations and ``k`` treatments is created from an ``(n, k)``-shaped matrix, as described in the [](../index.md) section.

<img alt="example.svg" src="example.svg" width="480">

```{eval-rst}
.. autoclass:: critdd.Diagram
   :members:
   :inherited-members:
```

## 2D sequences of CD diagrams

A sequence of ``m`` CD diagrams can be arranged in a single, 2-dimensional plot. The API for such a plot is similar to the API of [](#regular-cd-diagrams), but requires a tensor input of shape ``(m, n, k)`` and an optional list of ``m`` diagram names.

<img alt="2d_example.svg" src="2d_example.svg" width="480">

```{eval-rst}
.. autoclass:: critdd.Diagrams
   :members:
   :inherited-members:
```
