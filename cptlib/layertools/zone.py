from cptlib.layertools.layer import Layer
from cptlib.setuptools.measurement import UNITS


class Zone(Layer):
  """
  A vertical segment of the soil (layer) belonging to the same soil behaviour type (SBT) that starts at *top* and stops at *bottom*.

  A ValueError exception is raised during the initialization if *top* or *bottom* are negative or *bottom* < *top*.

  Zone objects can also be compared based on their thickness.
  """
  def __init__(self, number: int, top: float, bottom: float):
    """
    Parameters
    __________
    number: int
      The zone number that represents the SBT to which the layer of the soil belongs.
    top: float
      The depth at which the layer starts in the soil.
    bottom: float
      The depth at which the layer ends in the soil.
    """
    super().__init__(top, bottom)
    self._number: int = number

  def __repr__(self) -> str:
    return f'{self.__class__.__name__}(number={self._number},top={self._top},'\
    f'bottom={self._bottom})'

  def __str__(self) -> str:
    return f'Zone {self._number} starts at a depth of {"{:.3f}".format(self._top)} '\
    + UNITS['depth'] + f' and ends at {"{:.3f}".format(self._bottom)} ' + UNITS['depth']

  # ========== PUBLIC METHODS ==========
    
  @property
  def number(self) -> int:
    return self._number
  