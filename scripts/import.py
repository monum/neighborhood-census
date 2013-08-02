import os
import json
import requests
import pymongo
from pymongo import MongoClient

def load_config_json(filename):
    with open(filename, 'rt') as f:
        config = json.load(f)
        
    return config

def loadcounty():
    try:
        database.drop_collection('blocks')
    except:
        # database collection not yet made
        r = 1
    stats = [ "P0010001" ]
    full_list = ""
    tractlist = requests.get(("http://api.census.gov/data/2010/sf1?key=%s&get=NAME&" +
                "for=tract:*&in=state:%s+county:%s") % (API_KEY, STATE_CODE, COUNTY_CODE))
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
        stats_str = ','.join(stats)

        blocklist = requests.get(("http://api.census.gov/data/2010/sf1?key=%s&get=NAME," +
                     "%s&for=block:*&in=state:%s+county:%s+tract:%s")\
                     % (API_KEY, stats_str, STATE_CODE, COUNTY_CODE, tractname))
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

if __name__ == '__main__':
    if (os.environ.get('MONGOHQ_URL')):
        MONGO_URL = os.environ.get('MONGOHQ_URL')
        client = MongoClient(MONGO_URL)
    else:
        host = 'localhost'
        port = 27017
        client = MongoClient(host, port)
        
    database = client.ncensus
    
    config = load_config_json('configuration.json')
    STATE_CODE = config["STATE_CODE"]
    COUNTY_CODE = config["COUNTY_CODE"]
    API_KEY = config["API_KEY"]
    
    loadcounty()