from unittest import TestCase

from cptlib.layertools.layer import Layer


class TestLayer(TestCase):
  def test_value_error_top_negative(self):
    with self.assertRaises(ValueError):
      Layer(-5.0, 1.0)

  def test_value_error_top_greater_than_bottom(self):
    with self.assertRaises(ValueError):
      Layer(5.0, 1.0)

  def test_thickness_layer(self):
    expected_thickness: float = 4.0

    self.assertEqual(Layer(1.0, 5.0).thickness, expected_thickness)
