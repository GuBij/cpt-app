from unittest import TestCase

from cptlib.layertools.layers_probe import Layer, LayersProbe
from cptlib.probetools.probe_list import Probe, ProbeList

INPUT_FILE: str = 'cptlib/tests/input_files/test_layers_probe'

class TestLayersProbe(TestCase):
  def setUp(self):
    probes = ProbeList(INPUT_FILE)
    self._probe: Probe = probes[1]
    
    self.assertEqual(self._probe.number, '2000912_S2')
  
  def test_thickest_layer(self):
    expected_no_layers: int = 2
    expected_top: float = 2.945
    expected_bottom: float = 3.915
    
    layers = LayersProbe(self._probe, zone_number = 0, qc_max = 2.0)
    thickest_layer: Layer = max(layers)
    
    self.assertEqual(len(layers), expected_no_layers)
    self.assertAlmostEqual(thickest_layer.top, expected_top)
    self.assertAlmostEqual(thickest_layer.bottom, expected_bottom)

  def test_find_clay_layer(self):
    expected_no_layers: int = 1
    expected_top: float = 3.155
    expected_bottom: float = 3.205

    layers = LayersProbe(self._probe, zone_number = 3, qc_max = 2.0) # Zone 3 = Clay
    
    self.assertEqual(len(layers), expected_no_layers)
    for layer in iter(layers): # one layer = one iteration
      self.assertAlmostEqual(layer.top, expected_top)
      self.assertAlmostEqual(layer.bottom, expected_bottom)
  