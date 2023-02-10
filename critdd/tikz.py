"""A module for the Tikz export."""

import numpy as np
import os, re

def to_file(path, average_ranks, cliques, treatment_names, **kwargs):
    """Store the Tikz code in a file."""
    tikz_str = to_str(average_ranks, cliques, treatment_names, **kwargs)
    root, ext = os.path.splitext(path)
    if ext in [ ".tex", ".tikz" ]:
        with open(path, "w") as f:
            f.write(tikz_str) # store the Tikz code in a .tex or .tikz file
    elif ext in [ ".pdf", ".svg", ".png" ]:
        raise NotImplementedError(f"{ext} export is not yet implemented")
    else:
        raise ValueError("Unknown file path extension")

def to_str(average_ranks, cliques, treatment_names, *, title=None, reverse_x=False):
    """Return a string with Tikz code."""
    tikzpicture_options = [ # general styling
        "treatment line/.style={semithick, rounded corners=1pt}",
        "treatment label/.style={font=\\small, fill=white, text=black, inner xsep=5pt, outer xsep=-5pt}",
        "clique line/.style={ultra thick, line cap=round}",
    ]
    k = len(average_ranks)
    changepoint = np.ceil(k/2)
    axis_options = [
        "clip=false",
        "axis x line=center",
        "axis y line=none",
        "xmin=1",
        f"xmax={k}",
        f"ymin={-(changepoint+1.5)}",
        "ymax=0",
        "scale only axis",
        f"height={changepoint+2}\\baselineskip",
        "width=\\axisdefaultwidth",
        "ticklabel style={anchor=south, yshift=1.3*\\pgfkeysvalueof{/pgfplots/major tick length}, font=\\small}",
        "every tick/.style={yshift=.5*\\pgfkeysvalueof{/pgfplots/major tick length}}",
        "axis line style={-}",
        "title style={yshift=\\baselineskip}",
    ]
    if k <= 5:
        axis_options.append(f"xtick={{{','.join((np.arange(k)+1).astype(str))}}}")
    if reverse_x:
        axis_options.append("x dir=reverse")
    if title is not None:
        axis_options.append(f"title={{{title}}}")
    if not reverse_x and k % 2: # if k is odd
        changepoint -= 1
    changepoint -= 1
    commands = []
    for (i, j) in enumerate(np.argsort(average_ranks)): # add treatment commands
        xpos = 1 if i < changepoint else k
        if reverse_x:
            ypos = 2 + (i if i < changepoint else (k - i - (1.5 if k % 2 else 1)))
        else:
            ypos = (.5 if k % 2 else .0) + (i + .5 if i < changepoint else k - i + (1 if k % 2 else 1.5))
        commands.append(_treatment(
            treatment_names[j],
            average_ranks[j],
            xpos,
            ypos,
            reverse_x
        ))
    for i in range(len(cliques)):
        commands.append(_clique(
            np.min(average_ranks[cliques[i]]),
            np.max(average_ranks[cliques[i]]),
            1.5 * (i+1) / (len(cliques)+1)
        ))
    return _tikzpicture(_axis(*commands, options=axis_options), options=tikzpicture_options)

def _indent(content):
    return re.sub("^", "  ", content, flags=re.MULTILINE)
def _environment(name, *contents, options=[]):
    return "\n".join([
        f"\\begin{{{name}}}[",
        _indent(",\n".join(options)) + ",",
        "]\n",
        *contents,
        f"\n\\end{{{name}}}"
    ])
def _tikzpicture(*contents, options=[]):
    return _environment("tikzpicture", *contents, options=options)
def _axis(*contents, options=[]):
    return _environment("axis", *contents, options=options)
def _treatment(label, rank, xpos, ypos, reverse_x):
    anchor = "west" if (int(xpos == 1) + int(reverse_x)) % 2 == 0 else "east"
    return f"\\draw[treatment line] (axis cs:{rank}, 0) |- (axis cs:{xpos}, {-ypos})\n  node[treatment label, anchor={anchor}] {{{label}}};"
def _clique(minrank, maxrank, ypos):
    return f"\\draw[clique line] (axis cs:{minrank}, {-ypos}) -- (axis cs:{maxrank}, {-ypos});"
