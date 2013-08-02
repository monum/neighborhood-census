import os
import json
import requests
import pymongo
from pymongo import MongoClient

if (os.environ.get('MONGOHQ_URL')):
    MONGO_URL = os.environ.get('MONGOHQ_URL')
    client = MongoClient(MONGO_URL)
else:
    host = 'localhost'
    port = '27017'
    client = MongoClient(host, port)
    
database = client.ncensus

state_code = '25'
county_code = '025'

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

loadcounty()