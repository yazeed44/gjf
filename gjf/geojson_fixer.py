from enum import Enum

import geojson
import shapely.geometry
from geojson_rewind import rewind
from shapely.geometry import shape, mapping
from shapely.validation import make_valid


class FlipCoordinateOp(Enum):
    FLIP = 1
    NO_FLIPPING = 2
    FLIP_IF_ERROR = 3


# TODO update to include all types of numbers, including numpy's
def __is_vertex(array):
    return len(array) == 2 and \
           (isinstance(array[0], float) or isinstance(array[0], int))


# Convert from (latitude, longitude) to (longitude, latitude) format
# Supports any level of nesting
def flip_coordinates_order(geometry):
    if isinstance(geometry, dict):
        return {k: flip_coordinates_order(v) for k, v in geometry.items()}
    elif isinstance(geometry, list):
        return [geometry[1], geometry[0]] if __is_vertex(geometry) else [flip_coordinates_order(nested_arr) for
                                                                         nested_arr in geometry]
    else:
        return geometry


def __should_flip_coordinate_order(geometry):
    if isinstance(geometry, dict):
        return any([__should_flip_coordinate_order(v) for v in geometry.values()])
    elif isinstance(geometry, list):
        if not __is_vertex(geometry):
            return any([__should_flip_coordinate_order(nested_geometry) for nested_geometry in geometry])
    else:
        return False
    assert len(geometry) == 2

    coordinate = geometry

    min_long, max_long = -180, 180
    min_lat, max_lat = -85, 85.05112878

    is_current_coordinate_valid = min_long <= coordinate[0] <= max_long and min_lat <= coordinate[1] <= max_lat
    flipped_coordinate = [coordinate[1], coordinate[0]]
    is_flipped_coordinate_valid = min_long <= flipped_coordinate[0] <= max_long and min_lat <= flipped_coordinate[
        1] <= max_lat

    return not is_current_coordinate_valid and is_flipped_coordinate_valid


def __convert_tuples_of_tuples_to_list_of_lists(x):
    return list(map(__convert_tuples_of_tuples_to_list_of_lists, x)) if isinstance(x, (list, tuple)) else x


def __convert_tuples_to_lists_dict_recursive(x):
    if isinstance(x, tuple):
        return __convert_tuples_of_tuples_to_list_of_lists(x)
    elif isinstance(x, dict):
        return {k: __convert_tuples_to_lists_dict_recursive(v) for k, v in x.items()}
    elif isinstance(x, list):
        return [__convert_tuples_to_lists_dict_recursive(y) for y in x]
    else:
        return x


def __to_geojson(shapely_obj):
    geojson_mapping = __convert_tuples_to_lists_dict_recursive(mapping(shapely_obj))
    return geojson_mapping


def __to_shapely(geojson_obj):
    return shape(geojson_obj)


def apply_fixes_if_needed(geometry, flip_coords=FlipCoordinateOp.FLIP_IF_ERROR):
    # Handling Feature collection and Feature since they are not handled by Shapely
    if geometry["type"] == "FeatureCollection":
        return {"type": "FeatureCollection",
                "features": [apply_fixes_if_needed(feature, flip_coords) for feature in geometry["features"]]}
    elif geometry["type"] == "Feature":
        return {"type": "Feature", "geometry": apply_fixes_if_needed(geometry["geometry"])}
    if flip_coords == FlipCoordinateOp.FLIP or (
            flip_coords == FlipCoordinateOp.FLIP_IF_ERROR and __should_flip_coordinate_order(geometry)):
        geometry = flip_coordinates_order(geometry)
    valid_shapely = __to_shapely(geometry)
    if not valid_shapely.is_valid:
        valid_shapely = make_valid(valid_shapely)
        if isinstance(valid_shapely, shapely.geometry.Polygon) or isinstance(valid_shapely,
                                                                             shapely.geometry.MultiPolygon):
            valid_shapely = __to_shapely(rewind(__to_geojson(valid_shapely)))
    assert valid_shapely.is_valid
    return __to_geojson(valid_shapely)
