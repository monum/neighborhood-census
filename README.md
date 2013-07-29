heroku create neighborhood-census --stack cedar --buildpack https://github.com/monum/heroku-buildpack-python-gis.git

1. heroku run python
2. Test Shapely: 
    co = {"type": "Polygon", "coordinates": [[(-102.05, 41.0), (-102.05, 37.0), (-109.05, 37.0), (-109.05, 41.0)]]}
    lon, lat = zip(*co['coordinates'][0])
    from pyproj import Proj
    pa = Proj("+proj=aea +lat_1=37.0 +lat_2=41.0 +lat_0=39.0 +lon_0=-106.55")
    
    x, y = pa(lon, lat)
    cop = {"type": "Polygon", "coordinates": [zip(x, y)]}
    from shapely.geometry import shape
    shape(cop).area # Should give 268952044107.43506
