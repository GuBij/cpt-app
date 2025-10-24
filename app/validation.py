from pydantic import BaseModel


class Polygon(BaseModel):
    xy_min: tuple[int, int]
    xy_max: tuple[int, int]
    vertices: tuple[tuple[int, int], ...]

    class Config:
        json_schema_extra = {
            "example": {
                "xy_min": (107600, 171600),
                "xy_max": (112100, 174200),
                "vertices": ((107700, 173367), (110551, 173406), (111345, 174141), (112012, 173328), (112041, 171760),
                             (107680, 171681))
            }
        }
