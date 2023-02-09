```{toctree}
:hidden:

self
api
developer-guide
```

# Quickstart

This Python package generates Tikz code for publication-ready vector graphics.

Critical difference (CD) diagrams are a powerful tool to compare outcomes of multiple treatments over multiple observations. In machine learning research, for instance, we often compare the performance (= outcome) of multiple methods (= treatments) over multiple data sets (= observations).

**Regular CD diagrams:** statistically indistinguishable methods are connected.

<img alt="example.svg" src="example.svg" width="480">

**2D sequences:** sequences of multiple CD diagrams can be arranged in a single, 2-dimensional plot.

<img alt="2d_example.svg" src="2d_example.svg" width="480">


## Installation

```
pip install 'critdd @ git+https://github.com/mirkobunse/critdd'
```


## Usage

Basically, you use this package as follows:

```python
from critdd import TODO
```
