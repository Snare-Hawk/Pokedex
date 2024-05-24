from bs4 import BeautifulSoup as bs
import requests
import json
import xmltodict
import re

URL = "https://pokemondb.net/static/sitemaps/pokemondb.xml"
page = requests.get(URL)

reggie = "https\\:\\/\\/pokemondb\\.net\\/pokedex\\/[^(game|stats)].*"

# this gets the XML file
data = page.content

dataDict = xmltodict.parse(data)
masterList = []

for i in dataDict['urlset']['url']:
    if ('priority' in i):
        if re.search(reggie, i.get('loc')):
            masterList.append(i)

# written to a json for easier viewing
json_object = json.dumps(masterList, indent=4)

with open("jobs.json", "w+") as outfile:
	outfile.write(json_object)
