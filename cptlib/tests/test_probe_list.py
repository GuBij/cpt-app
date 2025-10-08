from unittest import TestCase

from cptlib.probetools.probe_list import ProbeList

INPUT_FILE: str = 'cptlib/tests/input_files/test_layers_probe'

class TestProbeList(TestCase):
  def test_read_records(self):
    expected_len_records: int = 1750
    
    records: list[dict] = ProbeList.read_records(INPUT_FILE)
    self.assertEqual(len(records), expected_len_records)

  def test_length_probe_list(self):
    expected_len_probes: int  = 2

    probes = ProbeList(INPUT_FILE)
    self.assertEqual(len(probes),expected_len_probes)

  def test_separate_probes(self):
    expected_probe_nrs: tuple[str,str] = ('2000912_S1','2000912_S2')
    expected_len_measurements: int = 875

    probes = ProbeList(INPUT_FILE)
    for index, probe in enumerate(probes):
      self.assertEqual(probe.number, expected_probe_nrs[index])
      self.assertEqual(len(probe.measurements), expected_len_measurements)
