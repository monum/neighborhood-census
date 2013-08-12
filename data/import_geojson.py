import os, pymongo, json
from pymongo import MongoClient

mongodb_uri = 'mongodb://localhost/ncensus'
connection = None
if(os.environ.has_key("MONGOLAB_URI")):
    mongodb_uri = os.environ.get("MONGOLAB_URI")
elif(os.environ.has_key("MONGOHQ_URL")):
    mongodb_uri = os.environ.get("MONGOHQ_URL")
    connection = MongoClient(mongodb_uri)
elif(os.environ.has_key("MONGODB_URI")):
    mongodb_uri = os.environ.get("MONGODB_URI")

try:
    if(connection is None):
        conn = mongodb_uri[ : mongodb_uri.rfind('/') + 1 ]
        connection = pymongo.Connection( conn )
        db = mongodb_uri[ mongodb_uri.rfind('/') + 1 : ]
        database = connection[ db ]
    else:
        db = mongodb_uri[ mongodb_uri.rfind('/') + 1 : ]
        database = connection[ db ]
except:
    print "MongoDB connection failed"
    connection = None

gj = json.load(open('blocks.geojson', 'r'))

for feature in gj["features"]:
    censusid = feature["properties"]["TRACTCE10"] + "/" + feature["properties"]["BLOCKCE"]
    
    if(feature["geometry"]["type"] == "MultiPolygon"):
        database.blocks.update({ "censusid": censusid }, { "$set": { "mpoly": feature["geometry"] }})    
    else:
        database.blocks.update({ "censusid": censusid }, { "$set": { "shape": feature["geometry"] }})
    
    print "mapped " + censusid