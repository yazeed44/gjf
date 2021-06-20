# gjf: A tool for fixing invalid GeoJSON objects

The goal of this tool is to make it as easy as possible to fix invalid GeoJSON objects through Python or Command Line.
## Installation
```shell
pip install gjf
```
Verify installation by running  
```shell
gjf --version
```
### Features
- Fix all types of GeoJSON objects, including FeatureCollection and Geometry Collection. If there is nothing to fix the object will be returned as is. 
- Can validate GeoJSON objects, and print explanations if the object is not valid.
- Can be used within Python or command line
## Usage
### Python
Say, you have a GeoJSON object defined as follows:
```python
obj = {"type":"Polygon","coordinates":[[[45.892166,25.697688],[45.894522,25.696483],[45.897131,25.695144],[45.898814,25.694268],[45.900496,25.693394],[45.901284,25.692983],[45.903946,25.697312],[45.894791,25.701933],[45.894621,25.701657],[45.892593,25.698379],[45.892166,25.697688]],[[45.892086,25.697729],[45.892166,25.697688],[45.892086,25.697729]]]}
```
You can simply call `apply_fixes_if_needed`
```python
from gjf.geojson_fixer import apply_fixes_if_needed

fixed_obj = apply_fixes_if_needed(obj)
```
You can also flip coordinates order by toggling `flip_coords`
```python
from gjf.geojson_fixer import apply_fixes_if_needed

fixed_obj_with_flipped_coordinates = apply_fixes_if_needed(obj, flip_coords=True)
```

You can also check whether a GeoJSON object is valid or not by calling `validity`
```python
from gjf.geojson_fixer import validity
validity(obj)
```
Will result `('invalid', ['Too few points in geometry component[45.892086 25.697729]', ''])`
### CLI
```shell
gjf invalid.geojson
```
`gjf` will fix the file, and output to `invalid_fixed.geojson` by default. If you need the output directed in another way you can use `--output-method` as directed below. It is also possible to fix multiple files, as below.
```shell
gjf invalid_1.geojson invalid_2.geojson
```
Above will output fixed GeoJSON objects to `invalid_1_fixed.geojson` and `invalid_2_fixed.geojson`. 
#### CLI Arguments
- `--version` print version and exit
- `--validate` validate GeoJSON file, and print the error message if it is not valid, without attempting to fix it.
- `--flip` Flip coordinates order
- `-o, --output-method [overwrite|new_file|print]`
  - Default is `new_file`, where `gjf` will output fixed GeoJSON object to file with the postfix `_fixed`. Whereas `overwrite` will write the fixed GeoJSON object to the source file, overwriting the original file in process. Lastly, `print` will output the fixed GeoJSON object on the terminal
  
```shell
gjf --output-method print invalid.geojson
```
This would print fixed `invalid.geojson` on the terminal

### Issues
Feel free to open an issue if you have any problems.

### Special Thanks
- [Shapely](https://github.com/Toblerity/Shapely)
- [geojson-rewind](https://github.com/chris48s/geojson-rewind)
