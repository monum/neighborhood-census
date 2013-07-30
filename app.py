import os, sys, pymongo, requests
from pymongo import MongoClient
from flask import Flask
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
def hello():
    return "Neighborhoods + Census"

def loadcounty():
    try:
        database.drop_collection('blocks')
    except:
        # database collection not yet made
        r = 1
    stats = [ "P0010001" ]
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
    allblocks = ""
    for block in contains:
      allblocks = allblocks + str(block)
    return allblocks
    
if __name__ == "__main__":
    app.run()