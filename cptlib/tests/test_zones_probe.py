from unittest import TestCase

from cptlib.layertools.zones_probe import Measurement, ZonesProbe
from cptlib.probetools.probe_list import ProbeList
from cptlib.setuptools.graph_set_up import GraphSetUp

INPUT_FILE_NAME: str = 'test_zone_'
INPUT_DIR: str = 'cptlib/tests/input_files/'

class TestZonesProbe(TestCase):
  def test_friction_ratio(self):
    expected_Rf: float = 1.3636363636363635
    
    probes = ProbeList(INPUT_DIR + INPUT_FILE_NAME + '4')
    meas: Measurement = probes[0].measurements[0]
    Rf: float = ZonesProbe.friction_ratio(meas)

    self.assertAlmostEqual(Rf, expected_Rf)

  def test_SBT_index(self):
    expected_I_SBT: float = 2.8659110243323247
    
    probes = ProbeList(INPUT_DIR + INPUT_FILE_NAME + '4')
    meas: Measurement = probes[0].measurements[0]
    Rf: float = ZonesProbe.friction_ratio(meas)
    I_SBT: float = ZonesProbe.SBT_index(Rf, meas.qc)

    self.assertAlmostEqual(I_SBT, expected_I_SBT)    
    
  def test_zone_number_SBT_Zone_4(self):
    expected_zone: int = 4
    expected_type: str = "Silt Mixtures"
    
    probes = ProbeList(INPUT_DIR + INPUT_FILE_NAME + str(expected_zone))
    meas: Measurement = probes[0].measurements[0]
    Rf: float = ZonesProbe.friction_ratio(meas)
    I_SBT: float = ZonesProbe.SBT_index(Rf, meas.qc)
    zone_nr: int = ZonesProbe.zone_number(Rf, meas.qc, I_SBT)
    
    self.assertEqual(zone_nr, expected_zone)
    self.assertEqual(ZonesProbe.SBT(expected_zone), expected_type)

  def test_zone_number_SBT_Zone_5(self):
    expected_zone: int = 5
    expected_type: str = "Sand Mixtures"

    probes = ProbeList(INPUT_DIR + INPUT_FILE_NAME + str(expected_zone))
    meas: Measurement = probes[0].measurements[0]
    Rf: float = ZonesProbe.friction_ratio(meas)
    I_SBT: float = ZonesProbe.SBT_index(Rf, meas.qc)
    zone_nr: int = ZonesProbe.zone_number(Rf, meas.qc, I_SBT)

    self.assertEqual(zone_nr, expected_zone)
    self.assertEqual(ZonesProbe.SBT(expected_zone), expected_type)

  def test_zone_number_SBT_Zone_6(self):
    expected_zone: int = 6
    expected_type: str = "Sands"

    probes = ProbeList(INPUT_DIR + INPUT_FILE_NAME + str(expected_zone))
    meas: Measurement = probes[0].measurements[0]
    Rf: float = ZonesProbe.friction_ratio(meas)
    I_SBT: float = ZonesProbe.SBT_index(Rf, meas.qc)
    zone_nr: int = ZonesProbe.zone_number(Rf, meas.qc, I_SBT)

    self.assertEqual(zone_nr, expected_zone)
    self.assertEqual(ZonesProbe.SBT(expected_zone), expected_type)

  def test_zone_number_SBT_Zone_8(self):
    expected_zone: int = 8
    expected_type: str = "Stiff Sand to Clayed Sand"

    probes = ProbeList(INPUT_DIR + INPUT_FILE_NAME + str(expected_zone))
    meas: Measurement = probes[0].measurements[0]
    Rf: float = ZonesProbe.friction_ratio(meas)
    I_SBT: float = ZonesProbe.SBT_index(Rf, meas.qc)
    zone_nr: int = ZonesProbe.zone_number(Rf, meas.qc, I_SBT)

    self.assertEqual(zone_nr, expected_zone)
    self.assertEqual(ZonesProbe.SBT(expected_zone), expected_type)

  def test_zone_number_SBT_Zone_9(self):
    expected_zone: int = 9
    expected_type: str = "Stiff Fine-Grained"

    probes = ProbeList(INPUT_DIR + INPUT_FILE_NAME + str(expected_zone))
    meas: Measurement = probes[0].measurements[0]
    Rf: float = ZonesProbe.friction_ratio(meas)
    I_SBT: float = ZonesProbe.SBT_index(Rf, meas.qc)
    zone_nr: int = ZonesProbe.zone_number(Rf, meas.qc, I_SBT)

    self.assertEqual(zone_nr, expected_zone)
    self.assertEqual(ZonesProbe.SBT(expected_zone), expected_type)

  def test_classify_SBT_Zone_0(self):
    expected_zone: int = 0
    expected_type: str = "Unknown"
    expected_top: float = 14.935
    expected_bottom: float = 15.035

    probes = ProbeList(INPUT_DIR + INPUT_FILE_NAME + str(expected_zone))
    zones = ZonesProbe(probes[0])
    for zone in iter(zones): # one iteration is expected
      self.assertAlmostEqual(zone.top, expected_top)
      self.assertAlmostEqual(zone.bottom, expected_bottom)
      self.assertEqual(zone.number, expected_zone)
    
    self.assertEqual(ZonesProbe.SBT(expected_zone), expected_type)

  def test_classify_Zone_8_7_bottom(self):
    expected_bottom: float = 12.165

    probes = ProbeList(INPUT_DIR + 'test_classify_zone_8_7')
    zones = ZonesProbe(probes[0])
    for counter, zone in enumerate(iter(zones)):
      if counter == 1:
        # verify value end_zone when condition 'start_zone == end_zone' is True
        self.assertAlmostEqual(zone.bottom, expected_bottom)

  def test_visualize_runtime_error(self):
    probes = ProbeList(INPUT_DIR + INPUT_FILE_NAME + '0')
    zones = ZonesProbe(probes[0])
    graph = GraphSetUp(file_name = '', indep_variable = 'fs')
    
    with self.assertRaises(RuntimeError):
      zones.visualize(graph)
  