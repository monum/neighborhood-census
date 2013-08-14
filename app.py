import os, sys, pymongo, requests, json
from pymongo import MongoClient
from flask import Flask, request, Response
from shapely.geometry import asShape

# Default Config
DEBUG = True

app = Flask(__name__)

state_code = '25'
county_code = '025'

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

@app.route("/")
def index():
    return "Neighborhoods + Census"

def loadcounty():
    try:
        database.drop_collection('blocks')
    except:
        # database collection not yet made
        r = 1
    # list statistics codes from http://www.census.gov/developers/data/sf1.xml
    stats = [ "P0010001", "P0120001", "P0120025", "P0120049", "P0420001", "P0420008" ]
    full_list = ""
    tractlist = requests.get('http://api.census.gov/data/2010/sf1?key=d343614e8f46717c1ffe54bd67ae76f6bf2c9b2d&get=NAME&for=tract:*&in=state:' + state_code + '+county:' + county_code)
    tractlist = tractlist.json()
    first_tract = True
    tractindex = 0
    for tract in tractlist:
        if(first_tract):
            # first row is a key row
            first_tract = False
            tractindex = tract.index("tract")
            continue
        tractname = tract[tractindex]

        blocklist = requests.get('http://api.census.gov/data/2010/sf1?key=d343614e8f46717c1ffe54bd67ae76f6bf2c9b2d&get=NAME,' + ','.join(stats) + '&for=block:*&in=state:' + state_code + '+county:' + county_code + '+tract:' + tractname)
        blocklist = blocklist.json()

        first_block = True
        blockindex = 0
        popindex = 0
        statindexes = { }
        for block in blocklist:
            if(first_block):
                # first row is a key row
                first_block = False
                blockindex = block.index("block")
                for stat in stats:
                    statindexes[ stat ] = block.index( stat )
                continue
            blockname = block[blockindex]
            
            blockstore = {
              'censusid': tractname + "/" + blockname,
            }
            for stat in stats:
              try:
                blockstore[ stat ] = int( block[ statindexes[stat] ] )
              except:
                blockstore[ stat ] = block[ statindexes[stat] ]
            database.blocks.insert(blockstore)
            
            full_list = full_list + tractname + "/" + blockname + "\n"
    return full_list

@app.route("/showone")
def showone():
    return str( database.blocks.find_one( ) )

@app.route("/showall")
def showall():
    allblocks = ""
    for block in database.blocks.find( ):
        allblocks = allblocks + str(block)
    return allblocks

@app.route("/intersect")
def intersect():
    latlng = request.args.get('latlng', '40,-70').split(',')
    latlng[0] = float(latlng[0])
    latlng[1] = float(latlng[1])
    latlng.reverse()
    contains = database.blocks.find({
      "shape": {
        "$geoIntersects": {
          "$geometry": {
            "type": "Point",
            "coordinates": latlng
          }
        }
      }
    }, {
      "_id": 0
    })
    allblocks = [ ]
    for block in contains:
      allblocks.append( block )
    return Response(json.dumps(allblocks),  mimetype='application/json')

@app.route("/within")
def within():    
    gj_geo = json.loads( request.args.get('geojson') )
    contains = database.blocks.find({
      "shape": {
        "$geoIntersects": {
          "$geometry": gj_geo
        }
      }
    }, {
      "_id": 0
    })
    allblocks = [ ]
    for block in contains:
      allblocks.append( block )
    return Response(json.dumps(allblocks),  mimetype='application/json')

@app.route("/estimate")
def estimate():
    gj_geo = json.loads( request.args.get('geojson') )
    allblocks = [ ]
    larger_bounds_shape = asShape(gj_geo)
    estimates = { }
    overestimates = { }
    contains = database.blocks.find({
      "shape": {
        "$geoIntersects": {
          "$geometry": gj_geo
        }
      }
    }, {
      "_id": 0
    })
    for block in contains:
      #allblocks.append( block )
      smaller_bounds = block["shape"]
      smaller_bounds_shape = asShape(smaller_bounds)
      smaller_bounds_area = smaller_bounds_shape.area
      intersection_area = smaller_bounds_shape.intersection(larger_bounds_shape).area
      overlap_proportion = float(intersection_area/smaller_bounds_area)
      
      for key in block:
        if(key == "shape" or key == "mpoly" or key == "censusid"):
          continue
        if(estimates.has_key(key)):
          estimates[key] = estimates[key] + overlap_proportion * block[key]
          overestimates[key] = overestimates[key] + block[key]
        else:
          estimates[key] = overlap_proportion * float(block[key])
          overestimates[key] = block[key]
      
      allblocks.append(smaller_bounds)
    for key in estimates:
      estimates[key] = round(estimates[key])
      
    return Response(json.dumps({ "blocks": allblocks, "estimate": estimates, "overestimate": overestimates }),  mimetype='application/json')

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
