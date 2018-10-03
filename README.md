Map-Extractor
Tested in ArcMap 10.3.1

Written by Ryan Crow and Tracey Felger, USGS

This script is used to extract geologic maps from an ArcSDE database. The script is custom designed for a modified version of NCGMP09, but we will be adapting it to fully comply with the current GEMS standards. All feature classes and feature datasets in the database should have the same prefix denoting the mapper or map product. The script then "clips" user specified feature classes to a quad boundary (this if provided as a polygon feature class with the field "Build" - all polygons with "yes" in "Build" are used as the quad boundary). A special approach using "select by location" is used to "clip" feature classes with feature linked annotations. Option routines allow for the building of polygons (from points and lines), the removal of multi-part lines, the building of topology, the creation of frequency tables, and the dropping of unneeded fields.
