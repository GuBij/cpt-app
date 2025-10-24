from collections import namedtuple

import requests
from bs4 import BeautifulSoup
from io import BytesIO
from shapely import wkt
from shapely.geometry import Point 

ProbeLocation = namedtuple('ProbeLocation', ['number','x_coord','y_coord'])

class ProbeLocationList:
  """
  A list of the probe locations laying within the rectangle with lower left corner *xy_min* and upper right corner *xy_max*. The probe locations are retrieved from the geoserver of 'Databank Ondergrond Vlaanderen (DOV)'.
  """
  def __init__(self, xy_min: tuple[int,int], xy_max: tuple[int,int]):
    """
    Parameters
    __________
    xy_min: tuple[int,int]
      The lower left corner of the rectangle that confines the search area.
    xy_max: tuple[int,int]
      The upper right corner of the rectangle that confines the search area.
    """
    self._xy_min: tuple[int, int] = xy_min
    self._xy_max : tuple[int, int] = xy_max
    self._locations: list[ProbeLocation] = []
    self.__retrieve_locations()

  def __getitem__(self, index: int) -> ProbeLocation:
    return self._locations[index]

  def __len__(self) -> int:
    return len(self._locations)
  
  def __repr__(self):
    return f'{self.__class__.__name__}(xy_min={self._xy_min}, xy_max={self._xy_max})'

  # ========== PRIVATE METHODS ==========

  def __retrieve_locations(self) -> None:
    """
    Retrieve the probe locations from the geoserver of DOV laying inside the rectangle spanned by *_xy_min* and *_xy_max* and assign them in a list to *_locations*.
    """
    URL: str = 'https://www.dov.vlaanderen.be/geoserver'
    URL_PATH: str = '/ows?service=WFS&version=1.0.0&request=GetFeature&typeName='\
    'dov-pub:Sonderingen&BBOX=' + '%g,%g,%g,%g' % (*self._xy_min, *self._xy_max) + \
    ',urn:ogc:def:crs:EPSG::31370'

    print('Retrieving probe locations from', URL, '...')

    page_content: bytes = requests.get(URL + URL_PATH).content
    soup = BeautifulSoup(page_content, "lxml-xml")

    x_coords: list[float] = [float(coord.string) for coord in 
                             soup.find_all('dov-pub:X_mL72')]
    y_coords: list[float] = [float(coord.string) for coord in 
                             soup.find_all('dov-pub:Y_mL72')]
    probe_numbers: list[str] = [nr.string for nr in 
                                soup.find_all('dov-pub:sondeernummer')]
    del soup

    print(f'\nRetrieved {len(x_coords)} probe locations that lay inside '\
          f'the rectangle spanned by {self._xy_min} and {self._xy_max}.')

    self._locations = list(map(lambda nr, x, y: ProbeLocation(nr,x,y), probe_numbers,
                               x_coords, y_coords))

  # ========== PUBLIC METHODS ==========

  def in_polygon(self, wkt_fmt: str, output_file_name: str = 
                        'in_polygon_output', bytesio: bool = False) -> BytesIO | None:
    """
    Extract the probe locations laying within the polygon *wkt_fmt* in WKT format and write the corresponding probe numbers to the text file *output_file_name*
    or to a BytesIO object if *bytesio* is True.
    """
    polygon = wkt.loads(wkt_fmt)
    
    indices: list[int] = []
    for counter, loc in enumerate(self._locations):
      if polygon.contains(Point(loc.x_coord, loc.y_coord)):
        indices.append(counter)

    if bytesio:
      content: str = ""
      for index in indices:
        content = content + f"\n{self._locations[index].number}"

      file_bytesio = BytesIO(content.encode('utf-8'))
      file_bytesio.seek(0)
      return file_bytesio

    with open(output_file_name + '.txt', 'w') as file:
      for index in indices:
        file.write("\n" + self._locations[index].number)

    print('\nProbes laying inside the polygon','\n\n\t', wkt_fmt, '\n\n',
          f'have been written to file {output_file_name}.txt')
