## Set up the instance

heroku create --stack cedar --buildpack https://github.com/monum/heroku-buildpack-python-gis.git

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

Run app.loadcounty() in Python. This will start inserting block data into the 'blocks' collection. 
You do not need to create a new collection for the blocks; Mongo will create the collection upon first use. You also do
not need to create a particular database.

Use web, Python, or other MongoDB tools to ensure a { "shape": "2dsphere" } index on your blocks collection e.g.,
    
    db.blocks.ensureIndex( { "shape":"2dsphere" } )

In the data directory, run import_geojson.py
