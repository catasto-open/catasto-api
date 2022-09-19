from pyproj import CRS, Transformer
from shapely.geometry import Point, box


def within_crs_bounds(epsg_code, lon, lat):
    """Returns `True` if point (`lon`, `lat`) is within the
    bounds of the given projection (`epsg_code`).
    Otherwise returns `False`."""
    crs = CRS.from_user_input(epsg_code)
    target_crs = "epsg:4326"
    bounding_box = box(*crs.area_of_use.bounds)
    if crs != target_crs:
        crs_transform = Transformer.from_crs(crs, target_crs)
        lat, lon = crs_transform.transform(lat, lon)

    return Point(lon, lat).within(bounding_box)
