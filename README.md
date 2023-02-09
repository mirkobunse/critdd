[![](https://img.shields.io/badge/docs-stable-blue.svg)](https://mirkobunse.github.io/critdd)
[![CI](https://github.com/mirkobunse/critdd/workflows/CI/badge.svg)](https://github.com/mirkobunse/critdd/actions)


# critdd | Critical Difference Diagrams

This Python package generates Tikz code for publication-ready vector graphics.

Critical difference (CD) diagrams are a powerful tool to compare outcomes of multiple treatments over multiple observations. In machine learning research, for instance, we often compare the performance (= outcome) of multiple methods (= treatments) over multiple data sets (= observations).

**Regular CD diagrams:** statistically indistinguishable methods are connected.

<img alt="docs/source/example.svg" src="docs/source/example.svg" width="480">

**2D sequences:** sequences of multiple CD diagrams can be arranged in a single, 2-dimensional plot.

<img alt="docs/source/2d_example.svg" src="docs/source/2d_example.svg" width="480">


## Installation

```
pip install 'critdd @ git+https://github.com/mirkobunse/critdd'
```


## Quick start

For detailed information, visit [the documentation](https://mirkobunse.github.io/critdd).

Basically, you use this package as follows:

```python
from critdd import TODO
```
