from shapely.geometry import asShape

larger_bounds = {"type": "Polygon", "coordinates": [[(-71.06686592102051, 42.353660080534574), 
(-71.0668659210205, 42.361207668593636), (-71.05399131774901, 42.361207668593636), 
(-71.05399131774901, 42.353660080534574), (-71.06686592102051,42.353660080534574)]]}

smaller_bounds = {"type": "Polygon", "coordinates": [[(-71.06094360351562, 42.35080571438234), 
(-71.06094360351562, 42.35803652353272), (-71.05038642883301, 42.35803652353272), 
(-71.05038642883301, 42.35080571438234), (-71.06094360351562,42.35080571438234)]]}

larger_bounds_shape = asShape(larger_bounds)
smaller_bounds_shape = asShape(smaller_bounds)

smaller_bounds_area = smaller_bounds_shape.area
intersection_area = smaller_bounds_shape.intersection(larger_bounds_shape).area

overlap_proportion = float(intersection_area/smaller_bounds_area)
