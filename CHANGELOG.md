# 0.1.2 (2021-06-22)
- Fixed bug where any field other than geometry is removed from Feature
- Raise an exception in case `gjf` is not able to fix the object
# 0.1.1 (2021-06-20)
- Fixed terminal not detecting `gjf` package

# 0.1.0 (2021-06-20)
- Fix all types of GeoJSON objects, including FeatureCollection and Geometry Collection. If there is nothing to fix the object will be returned as is. 
- Can validate GeoJSON objects, and print explanations if the object is not valid.
- Can be used within Python or command line
