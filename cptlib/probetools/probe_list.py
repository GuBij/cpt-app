import json
from collections import defaultdict
from typing import Iterator

from cptlib.probetools.probe import Probe
from cptlib.setuptools.decorators import filter
from cptlib.setuptools.measurement import Measurement


class ProbeList:
  """
  A list of the probes that are stored in the json file named *json_file_name*.
  
  Each record in the json file is expected to have at least the following four fields: 'diepte' (depth), 'qc' (cone resistance), 'fs' (sleeve friction) and 'sondeernummer' (probe number).
  """

  def __init__(self, json_file_name: str):
    """
    Parameter
    __________
    json_file_name: str
      Name of the json file containing the records of one or multiple probes without the file extension.
    """
    self._probes: dict[str, list[Measurement]] = defaultdict(list)
    self.__import_probe_data(json_file_name)

  def __getitem__(self, index: int) -> Probe:
    number: str = list(self._probes.keys())[index]
    measurements: list[Measurement] = list(self._probes.values())[index]
    return Probe(number, measurements)

  def __iter__(self) -> Iterator[Probe]:
    self._position: int = 0
    return self

  def __len__(self) -> int:
    return len(list(self._probes.keys()))

  def __next__(self) -> Probe:
    if self._position >= self.__len__():
      raise StopIteration()

    index: int = self._position
    self._position = self._position + 1
    return self.__getitem__(index)

  def __repr__(self) -> str:
    return f'{self.__class__.__name__} < {repr(self._probes)} >'

  # ========== PRIVATE METHODS ==========

  def __import_probe_data(self, json_file_name: str) -> None:
    records: list[dict] = self.read_records(json_file_name)
    self.__separate_probes(records)

    print(
        f"\nImported {len(records)} measurements from file {json_file_name}.json"
    )

  def __separate_probes(self, records: list[dict]) -> None:
    """
    Group the elements of *records* per probe and sort them statistically per probe based on the depth. The measurements of the probes in the _probe property are updated and a new prope is added if encountered. The latter one is accomplished by adding a new key to *_probe* containing the probe number and assigning a list of the measurements as the corresponding value.
    """
    for record in records:
      self._probes[record["sondeernummer"]].append(
          Measurement(record["diepte"], qc=record["qc"], fs=record["fs"]))

    for measurements in self._probes.values():
      measurements.sort(key=lambda x: x.depth)

  # ========== PUBLIC METHODS ==========

  def append(self, probe: Probe) -> None:
    """
    Add a new probe to the probe list. If the probe had already been added, a ValueError is raised.
    """
    if set(self._probes.keys()).intersection({probe.number}):
      raise ValueError(f"Probe with number {probe.number} had already been added "\
      "to the list.")

    for m in probe.measurements:
      self._probes[probe.number].append(m)

  @staticmethod
  @filter('diepte')
  def read_records(json_file_name: str) -> list[dict]:
    """
    Read the records from the json file and return them as dictionaries in a list.
    """
    records: list[dict] = []
    with open(json_file_name + ".json", 'r') as file:
      records = json.load(file)

    print(f"\nRead {len(records)} records from file {json_file_name}.json")

    return records
