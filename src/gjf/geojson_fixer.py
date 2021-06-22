from geojson_rewind import rewind
from shapely.geometry import shape, mapping
from shapely.validation import make_valid, explain_validity
from gjf import logger


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


def need_rewind(geojson_obj):
    # If rewind is generating a different object, that means we need to rewind
    return rewind(geojson_obj) != geojson_obj


def validity(geojson_obj):
    if geojson_obj["type"] == "FeatureCollection":
        collection_validity = [validity(feature) for feature in geojson_obj["features"]]
        final_txt = "valid" if all(
            [validity_tuple[0] == "valid" for validity_tuple in collection_validity]) else "invalid"
        final_explain = "" if final_txt == "valid" else [validity_tuple[1] for validity_tuple in collection_validity if
                                                         len(validity_tuple[1]) > 0]
        return final_txt, final_explain

    elif geojson_obj["type"] == "Feature":
        return validity(geojson_obj["geometry"])

    shapely_obj = __to_shapely(geojson_obj)
    valid_rewind_txt = "Polygons and MultiPolygons should follow the right-hand rule" if need_rewind(
        __to_geojson(shapely_obj)) else ""
    valid_txt = "valid" if (shapely_obj.is_valid and len(valid_rewind_txt) == 0) else "invalid"
    valid_explain = [explain_validity(shapely_obj), valid_rewind_txt] if valid_txt == "invalid" else []
    return valid_txt, valid_explain


def apply_fixes_if_needed(geojson_obj, flip_coords=False):
    # Handling Feature collection and Feature since they are not handled by Shapely
    if geojson_obj["type"] == "FeatureCollection":
        return {**geojson_obj,
                "features": [apply_fixes_if_needed(feature, flip_coords) for feature in geojson_obj["features"]]}
    elif geojson_obj["type"] == "Feature":
        return {**geojson_obj, "geometry": apply_fixes_if_needed(geojson_obj["geometry"])}
    if flip_coords:
        geojson_obj = flip_coordinates_order(geojson_obj)
    valid_shapely = __to_shapely(geojson_obj)
    if not valid_shapely.is_valid:
        logger.info("Geometry is invalid. Will attempt to fix with make_valid")
        valid_shapely = make_valid(valid_shapely)
    if need_rewind(__to_geojson(valid_shapely)):
        logger.info("Polygons within the geometry is not following the right-hand rule. Will attempt to fix with rewind")
        valid_shapely = __to_shapely(rewind(__to_geojson(valid_shapely)))
    if not valid_shapely.is_valid or need_rewind(__to_geojson(valid_shapely)):
        raise NotImplementedError(f"gjf is unable to fix this object. Please open a github issue to investigate")
    return __to_geojson(valid_shapely)
