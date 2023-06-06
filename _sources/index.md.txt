```{toctree}
:hidden:

self
manual
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

**Updating:** To update an existing installation of `critdd`, run

```
pip install --force-reinstall --no-deps 'critdd @ git+https://github.com/mirkobunse/critdd@main'
```

**Troubleshooting:** Starting from `pip 23.1.2`, you have to install `setuptools` and `wheel` explicitly. If you receive a "NameError: name 'setuptools' is not defined", you need to execute the following command before installing `critdd`.

```
pip install --upgrade pip setuptools wheel
```



## Usage

Basically, you use this package as follows:

```python
from critdd import Diagram
import pandas as pd

# download example data
_URL = "https://raw.githubusercontent.com/hfawaz/cd-diagram/master/example.csv"
df = pd.read_csv(_URL).pivot(
    index = "dataset_name",
    columns = "classifier_name",
    values = "accuracy"
)

# create a CD diagram from the Pandas DataFrame
diagram = Diagram(
    df.to_numpy(),
    treatment_names = df.columns,
    maximize_outcome = True
)

# inspect average ranks and groups of statistically indistinguishable treatments
diagram.average_ranks # the average rank of each treatment
diagram.get_groups(alpha=.05, adjustment="holm")

# export the diagram to a file
diagram.to_file(
    "example.tex",
    alpha = .05,
    adjustment = "holm",
    reverse_x = True,
    axis_options = {"title": "critdd"},
)
```


## Advanced usage: 2D diagrams

In the following, we create a 2-dimensional plot that represents a sequence of CD diagrams. During the process, we customize the style of the plot.

```python
from critdd import Diagrams # Diagrams is the 2D version of Diagram
import numpy as np
import pandas as pd

# download the example data
_URL = "https://raw.githubusercontent.com/mirkobunse/critdd/main/docs/source/2d_example.csv"
df = pd.read_csv(_URL)

# construct a sequence of CD diagrams
treatment_names = df["method"].unique()
diagram_names = df["diagram"].unique()
Xs = [] # collect an (n,k)-shaped matrix for each diagram
for n in diagram_names:
    diagram_df = df[df.diagram == n].pivot(
        index = "dataset",
        columns = "method",
        values = "loss"
    )[treatment_names] # ensure a fixed order of treatments
    Xs.append(diagram_df.to_numpy())
two_dimensional_diagram = Diagrams(
    np.stack(Xs),
    diagram_names = diagram_names,
    treatment_names = treatment_names,
    maximize_outcome = False
)

# customize the style of the plot and export to PDF
two_dimensional_diagram.to_file(
    "2d_example.pdf",
    preamble = "\n".join([ # colors are defined before \begin{document}
        "\\definecolor{color1}{HTML}{84B818}",
        "\\definecolor{color2}{HTML}{D18B12}",
        "\\definecolor{color3}{HTML}{1BB5B5}",
        "\\definecolor{color4}{HTML}{F85A3E}",
        "\\definecolor{color5}{HTML}{4B6CFC}",
    ]),
    axis_options = { # style the plot
        "cycle list": ",".join([ # define the markers for treatments
            "{color1,mark=*}",
            "{color2,mark=diamond*}",
            "{color3,mark=triangle,semithick}",
            "{color4,mark=square,semithick}",
            "{color5,mark=pentagon,semithick}",
        ]),
        "width": "\\axisdefaultwidth",
        "height": "0.75*\\axisdefaultheight",
        "title": "critdd"
    },
)
```
