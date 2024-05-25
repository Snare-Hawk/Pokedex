from bs4 import BeautifulSoup as bs
import requests
import json
import xmltodict
import re
from tkinter import *
from io import BytesIO
from PIL import Image, ImageTk

root = Tk()

def getName(url):
    newPage = requests.get(url)
    soup = bs(newPage.content, "html.parser")
    
    # get info from pkmn page
    pkmnName = soup.find("h1").text

    return pkmnName

def getImgLink(url):
    newPage = requests.get(url)
    soup = bs(newPage.content, "html.parser")

    # gets all images on the page and puts them into an array
    pkmnImg = soup.find_all("img")

    # we only need pkmnImg[1], at least for now
    pkmnImgLink = pkmnImg[1]['src']

    return pkmnImgLink

def urlToImage(url):
    response = requests.get(url)
    img_data = response.content
    img = Image.open(BytesIO(img_data))
    # Convert the image to a format Tkinter can use
    tk_img = ImageTk.PhotoImage(img)
    return tk_img

URL = "https://pokemondb.net/static/sitemaps/pokemondb.xml"
page = requests.get(URL)

reggie = "https\\:\\/\\/pokemondb\\.net\\/pokedex\\/[^(game|stats)].*"

# this gets the XML file
data = page.content

# make it a dict
dataDict = xmltodict.parse(data)

# initialize pkmnPageList to hold all the links
pkmnPageList = []

for i in dataDict['urlset']['url']:
    if ('priority' in i):
        if re.search(reggie, i.get('loc')):
            pkmnPageList.append(i)

# array of tkinter images
masterPkmnImgs = []

arrayOfDicts = []

for pkmnPage in pkmnPageList: 
    # gets the link to the pokemon's page 
    newURL = pkmnPage['loc']

    dictItem = {"name":getName(newURL), "img":getImgLink(newURL)}
    arrayOfDicts.append(dictItem)


# json_object = json.dumps(pkmnImg, indent=4)

# with open("pkmn.json", "w+") as outfile:
# 	outfile.write(json_object)

# root.title(pkmnName)
# root.geometry("500x500")

# Label(root, text="hi", font=("Ubuntu", 24)).pack()

"""
for i in masterPkmnImgs:
    # pkmnImg = urlToImage(pkmnImg[1]['src'])
    label = Label(root, image=i)
    label.pack()
"""
# for names, imgs in zip()
# root.mainloop()

# written to a json for easier viewing
json_object = json.dumps(arrayOfDicts, indent=4)

with open("PKMNinfo.json", "w+") as outfile:
	outfile.write(json_object)

print("Done!")