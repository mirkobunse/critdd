"""A module for the Tikz export of 2-dimensional axes."""

import numpy as np
import re
from . import tikz

TIKZPICTURE_OPTIONS = { # general styling
    "group line/.style": "semithick",
}

AXIS_OPTIONS = { # basic axis options, which don't depend on the diagram values
    "clip": "false",
    "grid": "both",
    "axis line style": "draw=none",
    "tick style": "draw=none",
    "xticklabel pos": "upper",
    "y dir": "reverse",
    "xmin": "0.5",
    "ymin": "0.66",
    "legend style": "draw=none,fill=none,at={(1.1,.5)},anchor=west,row sep=.25em,/tikz/every odd column/.append style={column sep=.5em}",
    "legend cell align": "left",
    "title style": "yshift=\\baselineskip",
    "width": "\\axisdefaultwidth",
}

def to_str(average_ranks, groups, treatment_names, diagram_names, *, reverse_x=False, as_document=False, tikzpicture_options=dict(), axis_options=dict(), preamble=None):
    """Return a string with Tikz code."""
    m, k = average_ranks.shape # numbers of diagrams and treatments
    changepoint = int(np.floor(k/2)) # index for breaking left and right treatments
    axis_defaults = AXIS_OPTIONS | { # diagram-dependent axis options
        "ytick": ",".join((np.arange(m)+1).astype(str)),
        "yticklabels": ",".join([ "{" + tikz._label(n) + "}" for n in diagram_names ]),
        "xmax": str(k + .5),
        "ymax": str(m + .66),
        "height": f"{.5 if m == 2 else m/5 if m < 5 else m/6}*\\axisdefaultheight",
    }
    if reverse_x:
        axis_defaults["x dir"] = "reverse"
    commands = [ _rank_plot(average_ranks[:,i], treatment_names[i]) for i in range(k) ]
    for i in range(m):
        for (j, g) in enumerate(groups[i]):
            commands.append(_group(
                np.min(average_ranks[i,g]),
                np.max(average_ranks[i,g]),
                i + (j+.66) / (1.33 * len(groups[i]) + 1) + 1
            ))
    tikz_str = tikz._tikzpicture(
        tikz._axis(*commands, options=axis_defaults | axis_options),
        options = TIKZPICTURE_OPTIONS | tikzpicture_options
    )
    if as_document:
        tikz_str = tikz._document(tikz_str, preamble=preamble)
    return tikz_str

def _rank_plot(average_ranks, treatment_name):
    return "\n".join([
        "\\addplot+[only marks] coordinates {",
        "  " + "\n  ".join([ f"({r}, {i+1})" for (i, r) in enumerate(average_ranks) ]),
        "};",
        "\\addlegendentry{" + tikz._label(treatment_name) + "}",
    ])
def _group(minrank, maxrank, ypos):
    return f"\\draw[group line] (axis cs:{minrank},{ypos}) -- ++(0pt,-3pt) -- ([yshift=-3pt]axis cs:{maxrank},{ypos}) -- ++(0pt,3pt);"
