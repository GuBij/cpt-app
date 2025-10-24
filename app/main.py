from collections import defaultdict
from fastapi import FastAPI, File, UploadFile, Path, Query, Body
from fastapi.responses import HTMLResponse, StreamingResponse
from pathlib import Path as Dir
from typing import Union, Annotated

from app.rate_limit import RateLimitMiddleware
from app.validation import Polygon
from cptlib.layertools.layers_probe import Layer, LayersProbe
from cptlib.layertools.zones_probe import ZonesProbe
from cptlib.probetools.probe_list import ProbeList
from cptlib.probetools.probe_location_list import ProbeLocationList
from cptlib.setuptools.graph_set_up import GraphSetUp

app = FastAPI(
  title="Cone Penetration Test Analyzer",
  description="Analyses probe measurements to determine the soil behaviour type according to the Robertson method (2010)."
)

INPUT_DIR = Dir('uploaded_files')
INPUT_DIR.mkdir(parents=True, exist_ok=True)

# Add rate limiting middleware to limit requests to 10 per minute
app.add_middleware(RateLimitMiddleware, throttle_rate=10)


def to_wkt(vertices: tuple[tuple[int, int], ...]) -> str:
  """
  Return a string representing the polygon formed by the tuple of vertices in **vertices** in WKT format.
  """
  wkt_fmt: str = "POLYGON (("
  for vertex in vertices:
    wkt_fmt = wkt_fmt + str(vertex[0]) + " " + str(vertex[1]) + ", "

  wkt_fmt = wkt_fmt + str(vertices[0][0]) + " " + str(vertices[0][1]) + "))"
  return wkt_fmt

@app.get("/")
def root() -> dict[str, str]:
  return {"Message": "Let's do a CPT analysis!"}

@app.delete("/clean/")
async def remove_uploaded_files() -> dict[str, str]:
  """
  Remove all files that have been uploaded to the server.
  """
  for file in INPUT_DIR.iterdir():
    if file.is_file():
      file.unlink()

  return {"Message": "Alle uploaded files have been successfully removed."}

@app.get("/probes/")
def upload_file() -> HTMLResponse:
    """
    An HTML form to upload a json file containing probes from Database Underground Flanders (DOV).
    """
    content = """
    <html>
        <body>
            <form action="/probes/upload/" enctype="multipart/form-data" method="post">
                <input type="file" name="json_probes_file">
                <button type="submit">Upload</button>
            </form>
        </body>
    </html>
    """
    return HTMLResponse(content=content)

@app.post('/probes/upload/')
async def save_file(json_probes_file: UploadFile = File(...)) -> dict[str, str]:
  """
  Save the uploaded json file on the server.
  """
  file_path: Dir = INPUT_DIR / json_probes_file.filename
  with open(file_path, 'wb') as buffer:
    content = await json_probes_file.read()
    buffer.write(content)

  return {"file path": str(file_path)}

@app.get("/probes/layers/{json_probes_file:path}")
async def info_layers(
        json_probes_file: Annotated[
          str,
          Path(
            title="JSON probes file",
            description="A JSON file containing probes from Database Underground Flanders (DOV).\
                        The extension .json should not be included."
          )
        ],
        zone_number: Annotated[
          int,
          Query(
            title="Zone number",
            description="A number between 0 and 9 representing the soil type.",
            ge=0,
            le=9
          )] = 0) -> dict[str, list[Union[str, int, float]]]:
  """
  Show the probe number, number of measurements, number of layers and the depth of the top and bottom from the thickest
  layer from each probe in **json_probes_file**.
  A layer is a vertical segment of the soil over which the cone resistance is smaller than 2.0 MPa.
  Optionally, the layer can be constrained to lay inside Zone **zone_number**.
  """
  probes = ProbeList(json_file_name=json_probes_file)  # list all the probes in the file
  probe_info: dict[str, list[Union[str, int, float]]] = defaultdict(list)

  for probe in probes:
    layers = LayersProbe(probe, zone_number) # find the clay layers in the probe
    probe_info["probe number"].append(probe.number)
    probe_info["# measurements"].append(len(probe.measurements))
    probe_info["# layers"].append(len(layers))
    probe_info["Soil behaviour type"].append(ZonesProbe.SBT(zone_number))

    if layers:
      thickest_layer: Layer = max(layers) # find thickest clay layer
      probe_info["top TL"].append(thickest_layer.top)
      probe_info["bottom TL"].append(thickest_layer.bottom)
    else:
      probe_info["top TL"].append("/")
      probe_info["bottom TL"].append("/")

  return probe_info

@app.get("/probes/zones/{json_probes_file:path}")
async def info_zones(
        json_probes_file: Annotated[
          str,
          Path(
            title="JSON probes file",
            description="A JSON file containing probes from Database Underground Flanders (DOV).\
                        The extension .json should not be included."
          )
        ]) -> dict[str, list[Union[str, int, float, set[str]]]]:
  """
  Show the probe number, number of measurements, number of zones and the soil behaviour types from each probe in **json_probes_file**.
  A zone is a vertical segment of the soil belonging to the same soil behaviour type.
  """
  probes = ProbeList(json_file_name=json_probes_file)  # list all the probes in the file
  probe_info: dict[str, list[Union[str, int, float, set[str]]]] = defaultdict(list)

  for probe in probes:
    zones = ZonesProbe(probe) # find the zone layers in the probe
    probe_info["probe number"].append(probe.number)
    probe_info["# measurements"].append(len(probe.measurements))
    probe_info["# zones"].append(len(zones))
    probe_info["Soil behaviour types (SBTs)"].append(zones.get_SBTs())

  return probe_info

@app.get("/probes/graph/{json_probes_file:path}")
async def graph_probes(
        json_probes_file: Annotated[
          str,
          Path(
            title="JSON probes file",
            description="A JSON file containing probes from Database Underground Flanders (DOV).\
                        The extension .json should not be included."
          )
        ]) -> StreamingResponse:
  """
  Show a graph displaying all the soil types, the cone resistance and the friction ratio versus the depth (m) based on
  the probe in **json_probes_file**.
  """
  probes = ProbeList(json_file_name=json_probes_file)  # list all the probes in the file
  for probe in probes:
    zones = ZonesProbe(probe)  # find the zone layers in the probe

    # Combine data from several objects into one graph
    graph = GraphSetUp(file_name=f"probe_{probe.number}", indep_variable='depth',
                       title=probe.number, legend_font_size='xx-small')
    probe.visualize(graph, ('qc', ''), (ZonesProbe.friction_ratio, 'Rf', '%', 'red'))
    zones.visualize(graph)

    return StreamingResponse(graph.save(bytesio=True), media_type="image/png")

@app.post("/probes/dov/")
async def retrieve_probes_in_polygon(
        poly: Annotated[
          Polygon,
          Body(
            title="Polygon object",
            description="A polygon confining the search area for the probes."
          )]) -> StreamingResponse:
  """
  Retrieve all probes from the geoserver of Database Underground Flanders (DOV) that are located in the area confined by **poly**.
  """
  probe_locations = ProbeLocationList(poly.xy_min, poly.xy_max)
  poly_wkt: str = to_wkt(poly.vertices)

  return StreamingResponse(probe_locations.in_polygon(wkt_fmt=poly_wkt, bytesio=True),
                           media_type="text/plain; charset=utf-8"
                           # for downloading: headers={"Content-Disposition": f"attachment; filename={file_name}.txt"}
                           )

@app.get("/SBT/")
async def info_sbt() -> dict[int, str]:
  """
  Show of each zone number the corresponding soil behaviour type.
  """
  zone_number_sbt: dict[int, str] = defaultdict(str)
  for k in range(0, 10):
    zone_number_sbt[k] = ZonesProbe.SBT(k)

  return zone_number_sbt
