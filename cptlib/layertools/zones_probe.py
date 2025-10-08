from collections.abc import Iterator
from math import exp, floor, log10, sqrt

from matplotlib.pyplot import Rectangle

from cptlib.layertools.zone import Zone
from cptlib.probetools.probe_list import Probe
from cptlib.setuptools.graph_set_up import GraphSetUp
from cptlib.setuptools.measurement import UNITS, Measurement

ATM_PRESS: float = 100.0 # kPa

class ZonesProbe:
  """
  The different soil behaviour types (SBTs) occurring in *probe* are determined and stored as zones in an object of this class. A zone is a vertical segment of the soil belonging to the same soil behaviour type.

  The different SBTs are Sensitive Fine-Grained, Organic Soils, Clays, Silt Mixtures, Sand Mixtures, Sands, Gravelly to Dense Sand, Stiff Sand to Clayed Sand, Stiff Fine-Grained. These are labelled as Zone 1 to Zone 9 respectively.

  An update to the Robertson method (1986), see Roberton et al. (2010), is used to determine the SBTs.
  """
  def __init__(self, probe: Probe):
    """
    Parameter
    _________
    probe: Probe
      The probe of which the SBTs need to be determined.
    """
    self._number: str = probe.number
    self._zones: list[Zone] = []
    self.__classify(probe.measurements)

  def __iter__(self) -> Iterator[Zone]:
    return iter(self._zones)

  def __len__(self) -> int:
    return len(self._zones)
  
  def __repr__(self) -> str:
    return f'{self.__class__.__name__} <probe: {self._number}>'

  def __str__(self) -> str:
    return f'\n\tProbe number: {self._number}\n\tNumber of zone layers: '\
    f'{self.__len__()}'

  # ========== PRIVATE METHODS ==========

  def __classify(self, measurements: list[Measurement]) -> None:
    """
    Determine the zones in the probe that supplies *measurements* and assign them in a list to the property _zones.
    """
    LEN_MEAS: int = len(measurements)
    current_zone_nr: int = -1
    start_zone: float = 0
    end_zone: float = 0
    for counter, m in enumerate(measurements, start = 1):
      m_zone_nr: int = -1
      try: # measurement can have NoneType
        m_Rf: float = self.friction_ratio(m)
      except TypeError:
        m_zone_nr = 0
      else:
        m_ISBT: float = self.SBT_index(Rf = m_Rf, qc = m.qc)
        m_zone_nr = self.zone_number(Rf = m_Rf, qc = m.qc, SBT_index = m_ISBT)
      finally:
        if counter == 1:
          current_zone_nr = m_zone_nr
          start_zone = m.depth
        elif counter == 2:
          start_zone = start_zone - 0.5*(m.depth - start_zone)
          
        if current_zone_nr != m_zone_nr: # current zone ends and new one begins
          end_zone = 0.5*(end_zone + m.depth)
          self._zones.append(Zone(current_zone_nr, start_zone, end_zone))
          current_zone_nr = m_zone_nr
          start_zone = end_zone
          
        if counter == LEN_MEAS: # last measurement: truncate the zone
          end_zone = 2*m.depth - start_zone if start_zone == end_zone else \
          m.depth + 0.5*(m.depth - end_zone)
          self._zones.append(Zone(current_zone_nr, start_zone, end_zone))
          
        end_zone = m.depth

  # ========== PUBLIC METHODS ==========

  @staticmethod
  def friction_ratio(measurement: Measurement) -> float:
    """Return the friction ratio in percent."""
    qc_kPa = 1000*measurement.qc # convert from MPa to kPa
    return measurement.fs*100/qc_kPa

  def get_SBTs(self) -> set[str]:
    """Return the SBTs that occur in the probe."""
    zone_nrs = []
    for zone in self._zones:
      zone_nrs.append(self.SBT(zone.number))
      
    return set(zone_nrs).difference({"Unknown"})

  @staticmethod
  def SBT(zone_number: int) -> str:
    """Map the zone number to the corresponding soil behaviour type."""
    soil_types: tuple = ("Unknown","Sensitive Fine-Grained", "Organic Soils", "Clays",
                         "Silt Mixtures", "Sand Mixtures", "Sands", 
                         "Gravelly to Dense Sand", "Stiff Sand to Clayed Sand",
                         "Stiff Fine-Grained")

    map_to_SBT: dict[int, str] = dict(zip(range(0,10), soil_types, strict=True))
    return map_to_SBT[zone_number]

  @staticmethod
  def SBT_index(Rf: float, qc: float) -> float:
    """Return the non-normalized Soil Behaviour Type Index."""
    qc_kPa = 1000*qc # convert from MPa to kPa
    a = 3.47 - log10(qc_kPa/ATM_PRESS)
    b = 1.22 + log10(Rf)

    return sqrt(a**2 + b**2)

  def visualize(self, graph: GraphSetUp) -> None:
    """
    Add a visual representation of the SBTs in the soil to *graph*. A runtime error is raised if *graph.indep_variable* doesn't equal 'depth'.

    Since this is a 1D graph only using the vertical axis, this function should only be called after all the plots using the horizontal axis have been added to *graph*.
    """
    if graph.indep_variable != 'depth':
      raise RuntimeError("graph.indep_variable must equal 'depth', but has the value"\
                         f" '{graph.indep_variable}'.")
    
    # https://www.learnui.design/tools/data-color-picker.html
    COLORS: tuple = ('w','k','#003f5c','#2f4b7c','#665191','#a05195','#d45087','#f95d6a'
                     ,'#ff7c43','#ffa600')
    
    X_MAX: float
    _ , X_MAX = graph.xlim()
    NO_ZONES: int = self.__len__()
    
    for zone in self._zones:
      graph.axes.add_patch(Rectangle((0, -zone.bottom), X_MAX, zone.thickness,
                                     facecolor = COLORS[zone.number], 
                                     label = self.SBT(zone.number)))

    graph.ylim(-self._zones[NO_ZONES-1].bottom, -floor(self._zones[0].top/10)*10)
    graph.free_yticklabels_from_minus()
    graph.legend(True)

  def write(self, file_name: str) -> None:
    """Write the zone distribution of the soil to the text file *file_name*."""
    with open(file_name + ".txt", 'w') as file:
      for zone in self._zones:
        file.write("\n" + str("{:.3f}".format(zone.top)) + " " + UNITS['depth'] + 
                   " - " + str("{:.3f}".format(zone.bottom)) + " " + UNITS['depth']
                   +  " : " + self.SBT(zone.number) + " (Zone " + str(zone.number) +
                   ")")

    print("\nThe result of the SBT classification has been written to file",
          file_name + ".txt.")

  @staticmethod
  def zone_number(Rf: float, qc: float, SBT_index: float) -> int:
    """
    Determine the SBT using the updated Robertson method and return the corresponding zone number.
    """
    qc_kPa = 1000*qc # convert from MPa to kPa
    threshold = 1.0/(0.006*(Rf-0.9)-0.004*(Rf-0.9)**2-0.005)
    if Rf > 4.5 and qc_kPa/ATM_PRESS >= threshold:
      return 9
    elif Rf > 1.5 and Rf <= 4.5 and qc_kPa/ATM_PRESS >= threshold:
      return 8
    elif qc_kPa/ATM_PRESS < 12*exp(-1.4*Rf):
      return 1
    elif SBT_index > 3.6:
      return 2
    elif SBT_index > 2.95:
      return 3
    elif SBT_index > 2.6:
      return 4
    elif SBT_index > 2.05:
      return 5
    elif SBT_index > 1.31:
      return 6
    else:
      return 7
