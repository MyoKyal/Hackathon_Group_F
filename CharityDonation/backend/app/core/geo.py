from geoalchemy2.elements import WKTElement
from sqlalchemy import func, select
from sqlalchemy.orm import Session


def make_point(lat: float, lng: float) -> WKTElement:
    return WKTElement(f"POINT({lng} {lat})", srid=4326)


def extract_lat_lng(db: Session, geography_column) -> tuple[float, float]:
    wkt = db.scalar(select(func.ST_AsText(geography_column)))
    if not wkt:
        return 0.0, 0.0
    coords = wkt.replace("POINT(", "").replace(")", "").split()
    lng, lat = float(coords[0]), float(coords[1])
    return lat, lng
