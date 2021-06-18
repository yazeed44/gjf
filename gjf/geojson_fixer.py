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
def flip_coordinates_order(coords_array):
    if __is_vertex(coords_array):
        return [coords_array[1], coords_array[0]]
    return [flip_coordinates_order(nested_arr) for nested_arr in coords_array]


def __should_flip_coordinate_order(geometry_coordinate):
    if not __is_vertex(geometry_coordinate):
        return __should_flip_coordinate_order(geometry_coordinate[0])
    elif len(geometry_coordinate) == 0:
        return False
    coordinate = geometry_coordinate

    assert len(coordinate) == 2
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


# TODO handle Collections
def apply_fixes_if_needed(geometry, flip_coords=FlipCoordinateOp.FLIP_IF_ERROR):
    # TODO handle flipping collections coordinates
    if flip_coords == FlipCoordinateOp.FLIP or (
            flip_coords == FlipCoordinateOp.FLIP_IF_ERROR and __should_flip_coordinate_order(geometry["coordinates"])):
        cords = flip_coordinates_order(geometry["coordinates"])
    else:
        cords = geometry["coordinates"]
    # FIXME do not assume coordinates is gonna be on the top of the hierarchy
    cur_geojson = {"type": geometry["type"], "coordinates": cords}
    valid_shapely = __to_shapely(cur_geojson)
    if not valid_shapely.is_valid:
        valid_shapely = make_valid(valid_shapely)
        if isinstance(valid_shapely, shapely.geometry.Polygon) or isinstance(valid_shapely,
                                                                             shapely.geometry.MultiPolygon):
            valid_shapely = __to_shapely(rewind(__to_geojson(valid_shapely)))
    assert valid_shapely.is_valid
    return __to_geojson(valid_shapely)
