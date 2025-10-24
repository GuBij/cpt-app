import warnings
from typing import Any

import matplotlib.axes as axs
import matplotlib.figure as fig
import matplotlib.pyplot as plt

from io import BytesIO
from matplotlib.text import Text

from cptlib.setuptools.measurement import QUANTITIES, UNITS


class GraphSetUp:
  """
  A graph of the probe's content w.r.t. the independent quantity *indep_variable* on the vertical axes and with *title*. The graph can be stored in a png file named *file_name*.

  A ValueError exception will occur if *indep_variable* takes a value other than 'depth', 'qc' or 'fs'.

  All the methods from the pyplot module can be called by an instance of this class.
  """
  def __init__(self, file_name: str, indep_variable: str, title: str = '', legend_font_size: str = 'medium'):
    """
    Parameters
    __________
    file_name: str
      The name of the file in which the graph will be stored.
    indep_variable: str
      The name of the independent quantity in the plot.
    title: str, default: ''
      The title that appears on top of the plot.
    font_size: str, default: 'medium'
      The font size of the legend labels, i.e., 'xx-small', 'x-small', 'small', 'medium', 'large', 'x-large' or 'xx-large'.
    """
    if not set(QUANTITIES).intersection({indep_variable}):
      raise ValueError(f"Class '{self.__class__.__name__}' cannot be instantiated"\
      " since the value of input argument 'indep_variable' is invalid. It should"\
      f" take one of the following values: {QUANTITIES}")
    
    self._fig: fig.Figure
    self._axes: axs._axes.Axes
    self._fig, self._axes = plt.subplots(layout='constrained')
    self._file_name: str = file_name
    self._indep_variable: str = indep_variable
    self._legend_font_size = legend_font_size
    
    self._axes.set_title(title)
    self._axes.set_ylabel(indep_variable + ' [' + UNITS[indep_variable] + ']')

  def __getattr__(self, name: str) -> Any:
    return getattr(plt, name)

  def __repr__(self) -> str:
    return f'{self.__class__.__name__}(file_name={self._file_name}, indep_variable='\
    f'{self._indep_variable}, title={self._axes.get_title()})'

  # ========== PUBLIC METHODS ==========

  @property
  def axes(self) -> axs._axes.Axes:
    return self._axes

  def free_yticklabels_from_minus(self) -> None:
    """Remove the minus sign from the ytick labels."""
    new_yticklabels: list[Text] = []
    for ylabel in self._axes.get_yticklabels():
      ylabel.set_text(ylabel.get_text().replace(u"\u2212", ""))
      new_yticklabels.append(ylabel)

    with warnings.catch_warnings():
      warnings.simplefilter("ignore")
      self._axes.set_yticklabels(new_yticklabels)

  @property
  def indep_variable(self) -> str:
    return self._indep_variable

  def legend(self, outside_fig: bool = False) -> None:
    """
    Update the legend of the figure. 

    Parameters
    __________
    outside_fig: bool, default: False
      The legend is placed next to the graph area if its value is True.
    """
    # Remove all the duplicated labels
    handles: list
    labels: list
    handles, labels = self._axes.get_legend_handles_labels()
    by_label: dict = dict(zip(labels, handles, strict = True))

    if outside_fig:
      if self._axes.get_legend():
        self._axes.get_legend().remove()        
      pos = self._axes.get_position()
      self._axes.set_position((pos.x0, pos.y0, pos.width * 0.85, pos.height))
      self._fig.legend(list(by_label.values()), list(by_label.keys()), 
                        loc='outside center right', fontsize=self._legend_font_size)
    else:
      self._axes.legend(list(by_label.values()), list(by_label.keys()),
                        fontsize=self._legend_font_size)

  def save(self, bytesio: bool = False) -> BytesIO | None:
    "Save the figure to a png file named *_file_name* or to a png BytesIO object if *bytesio* is *True*."
    if bytesio:
      bytesio_fig = BytesIO()
      self._fig.savefig(bytesio_fig, format='png')
      bytesio_fig.seek(0)
      return bytesio_fig
    else:
      self._fig.savefig(self._file_name + '.png')
