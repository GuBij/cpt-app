from cptlib.setuptools.measurement import UNITS


class Layer:
  """
  A vertical segment of the soil that starts at *top* and stops at *bottom*.

  A ValueError exception is raised during the initialization if *top* is negative or *bottom* < *top*.

  Layer objects can also be compared based on their thickness.
  """
  def __init__(self, top: float, bottom: float):
    """
    Parameters
    __________
    top: float
      The depth at which the layer starts in the soil.
    bottom: float
      The depth at which the layer ends in the soil.
    """
    if top < 0 or bottom < top:
      raise ValueError("Parameters 'top' and 'bottom' of class 'Layer' are required"\
                       "to be positive and 'top' < 'bottom'.")
    
    self._top: float = top
    self._bottom: float = bottom

  def __gt__(self, other: "Layer") -> bool:
    return self.thickness > other.thickness

  def __lt__(self, other: "Layer") -> bool:
    return self.thickness < other.thickness

  def __ge__(self, other: "Layer") -> bool:
    return self.thickness >= other.thickness

  def __le__(self, other: "Layer") -> bool:
    return self.thickness <= other.thickness

  def __eq__(self, other: "Layer") -> bool:
    return self.thickness == other.thickness

  def __ne__(self, other: "Layer") -> bool:
    return self.thickness != other.thickness

  def __repr__(self) -> str:
    return f'{self.__class__.__name__}(top={self._top}, bottom={self._bottom})'

  def __str__(self) -> str:
    return f'Layer starts at a depth of {"{:.3f}".format(self._top)} '\
    + UNITS['depth'] + f' and ends at {"{:.3f}".format(self._bottom)} '\
    + UNITS['depth']

  # ========== PUBLIC METHODS ==========

  @property
  def bottom(self) -> float:
    return self._bottom
  
  @property
  def thickness(self) -> float:
    """Return the difference in depth between the bottom and top of the layer."""
    return self._bottom - self._top

  @property
  def top(self) -> float:
    return self._top
