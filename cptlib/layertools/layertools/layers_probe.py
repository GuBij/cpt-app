from collections.abc import Iterator

from cptlib.layertools.layer import Layer
from cptlib.layertools.zones_probe import ZonesProbe
from cptlib.probetools.probe_list import Probe
from cptlib.setuptools.measurement import Measurement


class LayersProbe:
  """
  All the layers of *probe* are determined by and stored in an object of this class. A probe layer is a vertical segment of the soil such that ``qc < *qc_max*``. Optionally, the layer can be constrained to lay inside Zone *zone_number*.
  """
  def __init__(self, probe: Probe, zone_number: int = 0, qc_max: float = 2.0):
    """
    Parameters
    __________
    probe: Probe
      The probe of which the layers need to be determined.
    zone_number: int, default: 0
      The zone number of the layers.
    qc_max: float, default: 2.0
      The maximum allowable value of qc in a layer.
    """
    self._qc_max: float = qc_max
    self._number: str = probe.number
    self._zone_number: int = zone_number
    self._layers: list[Layer] = []
    self.__find_layers(probe.measurements)

  def __iter__(self) -> Iterator[Layer]:
    return iter(self._layers)

  def __len__(self) -> int:
    return len(self._layers)

  def __repr__(self) -> str:
    return f'{self.__class__.__name__} < zone_number={self._zone_number}, '\
    f'qc_max={self._qc_max}, probe: {self._number}>'

  def __str__(self) -> str:
    return f'\n\tProbe number: {self._number}\n\tNumber of layers: {self.__len__()} ' \
    f'\t( qc < {self._qc_max} MPa)'

  # ========== PRIVATE METHODS ==========

  def __find_layers(self, measurements: list[Measurement]) -> None:
    """
    Determine the layers of type Zone *zone_number* for which ``qc < 2 MPa`` in the probe that has supplied *measurements* and assign them in a list to the property _layers.
    """
    LEN_MEAS: int = len(measurements)
    in_layer: bool = False
    start_layer: float = 0
    end_layer: float = 0
    in_zone: bool = True
    m_zone_nr: int = self._zone_number
    for counter, m in enumerate(measurements, start = 1):
      if counter == 2 and in_layer:
        start_layer = end_layer - 0.5*(m.depth - end_layer)

      if m_zone_nr > 0:
        try: # measurement can have NoneType
          m_Rf: float = ZonesProbe.friction_ratio(m)
        except TypeError:
          in_zone = False
        else:
          m_ISBT: float = ZonesProbe.SBT_index(m_Rf, m.qc)
          m_zone_nr: int = ZonesProbe.zone_number(m_Rf, m.qc, m_ISBT)
          in_zone = bool(m_zone_nr == self._zone_number)

      check_in_layer: bool = False
      try: # m.qc can have NoneType
        check_in_layer = m.qc < self._qc_max
      except TypeError:
        pass
      else:
        if check_in_layer and in_zone and not in_layer: # enter the layer
          in_layer = True
          start_layer = 0.5*(end_layer + m.depth)
        elif (not check_in_layer or not in_zone) and in_layer: # leave the layer
          in_layer = False
          end_layer = 0.5*(end_layer + m.depth)
          self._layers.append(Layer(start_layer, end_layer))
      
      if counter == LEN_MEAS and in_layer: # last measurement: truncate the layer
        end_layer = m.depth + 0.5*(m.depth - end_layer)
        self._layers.append(Layer(start_layer, end_layer))

      end_layer = m.depth
