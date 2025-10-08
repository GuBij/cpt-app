from collections import defaultdict
from typing import Union

import pandas as pd

from cptlib.layertools.layers_probe import Layer, LayersProbe
from cptlib.layertools.zones_probe import ZonesProbe
from cptlib.probetools.probe_list import ProbeList
from cptlib.probetools.probe_location_list import ProbeLocationList
from cptlib.setuptools.graph_set_up import GraphSetUp


def print_info(info_dict: dict, show: bool, **kwargs) -> None:
  if show:
    print("\n",pd.DataFrame(info_dict).to_string(index=False))
    print("\n (TL = thickest layer)")
  else:
    for key, value in kwargs.items():
      info_dict[key].append(value)


if __name__ == '__main__':
  INPUT_DIR: str = '../input_files/'
  OUTPUT_DIR: str = '../output_files/'
  
  print("\nTASK 1\n")
  probes = ProbeList(json_file_name=INPUT_DIR + 'opdracht1') # list all the probes in the file  
  probe_info: dict[str, list[Union[str, int, float]]] = defaultdict(list)
  
  for probe in probes:
    layers = LayersProbe(probe) # find the layers in the probe
    print_info(
      probe_info, False, **{"probe number": probe.number, "# measurements":
                           len(probe.measurements), "# layers": len(layers)})
    if layers:
      thickest_layer: Layer = max(layers) # find thickest layer
      print_info( probe_info, False, **{"top TL": thickest_layer.top,
                                             "bottom TL": thickest_layer.bottom})
    else:
      print_info( probe_info, False, **{"top TL": "/", "bottom TL": "/"})
    
  print_info(probe_info, True)
  
  print("\nTASK 1a: identify the thickest clay layer")
  del probe_info
  probe_info: dict[str, list[Union[str, int, float]]] = defaultdict(list)
  
  for probe in probes:
    layers = LayersProbe(probe, zone_number=3) # find the clay layers in the probe
    print_info(
      probe_info, False, **{"probe number": probe.number, "# measurements":
                           len(probe.measurements), "# layers": len(layers)})
    if layers:
      thickest_layer: Layer = max(layers) # find thickest clay layer
      print_info( probe_info, False, **{"top TL": thickest_layer.top,
                                              "bottom TL": thickest_layer.bottom})
    else:
      print_info( probe_info, False, **{"top TL": "/", "bottom TL": "/"})

  print_info(probe_info, True)

  print("\nTASK 2\n")
  del probe_info
  probe_info: dict[str, list[Union[str, int, float]]] = defaultdict(list)
  
  probes = ProbeList(json_file_name=INPUT_DIR + 'opdracht2') # list all the probes in the file
  for probe in probes:
    zones = ZonesProbe(probe) # find the zone layers in the probe
    print_info(
      probe_info, False, **{"probe number": probe.number, "# measurements":
                            len(probe.measurements), "# zone layers": len(zones)})
    print_info(probe_info, True)
    print("\nSoil behaviour types: ", zones.get_SBTs())
    zones.write(OUTPUT_DIR + "task2_SBTs")
    
    # Combine data from several objects into one graph
    graph = GraphSetUp(file_name=OUTPUT_DIR + 'task2', indep_variable='depth',
                       title=probe.number, legend_font_size='xx-small')
    probe.visualize(graph, ('qc',''), (ZonesProbe.friction_ratio,'Rf','%','red'))
    zones.visualize(graph)
    #graph.save()

  print("\nTASK 3\n")
  probe_locations = ProbeLocationList((107600,171600),(112100,174200))

  polygon: str = "POLYGON ((107700 173367, 110551 173406, 111345 174141,"\
  "112012 173328, 112041 171760, 107680 171681, 107700 173367))"
  probe_locations.in_polygon(wkt_fmt = polygon, output_file_name = OUTPUT_DIR +
                                    'task3')
  