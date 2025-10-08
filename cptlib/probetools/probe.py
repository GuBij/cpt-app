from inspect import isfunction
from math import ceil
from types import NoneType
from typing import Union

from cptlib.setuptools.graph_set_up import GraphSetUp
from cptlib.setuptools.measurement import COLORS, QUANTITIES, UNITS, Measurement


class Probe:
  """
  A container that stores the measurements of the probe and its identification number *number*. It also offers functionality to visualize the probe's content.
  """
  def __init__(self, number: str, measurements: list[Measurement]):
    """
    Parameters
    __________
    number: str
      The identification number of the probe.
    measurements: list[Measurement]
      A list containing all the measurements of the probe.
    """
    self._number: str = number
    self._measurements: list[Measurement] = measurements

  def __repr__(self) -> str:
    return f'{self.__class__.__name__}(number={self._number}, measurements='\
    f'{self._measurements})'

  # ========== PUBLIC METHODS ==========

  @property
  def measurements(self) -> list[Measurement]:
    return self._measurements

  @property
  def number(self) -> str:
    return self._number

  def visualize(self, graph: GraphSetUp, *argv) -> None:
    """
    Add vertical line plots of the QUANTITIES in *argv w.r.t. the quantity *graph.indep_variable* to *graph*.

    Parameters
    __________
    graph: GraphSetUp
      The graph object.
    *argv
      The QUANTITIES that need to be plotted w.r.t. the quantity *graph.indep_variable*
      They need to be passed on in a tuple of which the first component contains 'depth', 'qc', 'fs' or a function of these QUANTITIES that accepts a Measurement object. The second component contains the label to be displayed in the graph. In case a function is passed on in the first component, a third and fourth component are required that contain the unit and line color for the graph resp.

      If the label (second component) is an empty string, the standard representation of the quantity will be used as label in the graph. If the first component is a function, however, a label is required and '<?>' will be displayed if not provided.
    """
    indep_values: list[Union[float, NoneType]] = []
    sign: int = 1
    if graph.indep_variable == 'depth':
      sign = -1 # for visualization purposes
    
    for measurement in self._measurements:
      try: # measurement can be NoneType
        indep_values.append(
          sign*dict(zip(QUANTITIES, measurement, strict = True))[graph.indep_variable])
      except TypeError:
        indep_values.append(None)

    x_max: float = 0.0
    for arg in argv:
      x_values: list[Union[float, NoneType]] = []
      unit: str = ''
      color: str = ''
      arg_label: str = arg[1]
      
      if isfunction(arg[0]):
        unit = arg[2]
        color = arg[3]
        if not arg_label:
          arg_label = '<?>' # label must be present in this case
        for measurement in self._measurements:
          try: # measurement can be NoneType
            x_values.append(arg[0](measurement))
          except TypeError:
            x_values.append(None)
          
      else:
        unit = UNITS[arg[0]]
        color = COLORS[arg[0]]
        for measurement in self._measurements:
          x_values.append(dict(zip(QUANTITIES, measurement, strict = True))[arg[0]])
        
      graph.axes.plot(x_values, indep_values, color, label = arg_label +\
                      ' [' + unit + ']' if arg_label else arg[0] + ' [' + unit + ']')

      x_max_arg: float = max([x_value for x_value in x_values if x_value]) #Remove None
      x_max = x_max_arg if x_max < x_max_arg else x_max

    graph.xlim(0, ceil(x_max/10.0)*10)
    graph.legend()
    graph.grid(True)
  