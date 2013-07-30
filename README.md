heroku create neighborhood-census --stack cedar --buildpack https://github.com/monum/heroku-buildpack-python-gis.git


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