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

## MongoHQ addon for Heroku

Free sandbox level of MongoDB from MongoHQ:

    heroku addons:add mongohq:sandbox

## Census GeoJSON

Download 2010 Census block shapefile from TIGER. On http://www.census.gov/geo/maps-data/data/tiger-data.html

- Select the last option: 2010 Census Population & Housing Unit Counts -- Blocks

- Select your state or DC from the dropdown

- Click GO to download a zipped shapefile

- Open the shapefile in QGIS, ArcGIS (with Esri2Open toolbar), or another GIS tool.

- Select all blocks with COUNTYFP10 equal to your county's ID (for example, '025')

- Save selection as data/blocks.geojson in WGS84/EPSG:4326 projection and GeoJSON format.

## Census API

Get your own API key here:

http://www.census.gov/developers/tos/key_request.html

Find the codes for each state using:

http://api.census.gov/data/2010/sf1?key=d343614e8f46717c1ffe54bd67ae76f6bf2c9b2d&get=NAME&for=state:*

Once you have the number for the state, modify this URL to list all counties in your state:

http://api.census.gov/data/2010/sf1?key=d343614e8f46717c1ffe54bd67ae76f6bf2c9b2d&get=NAME&for=county:*&in=state:25

Once you have the number for your county, modify these lines in app.py:

    state_code = '25'
    county_code = '025'
