import fileinput
import json
import os
import re
from pathlib import Path
from tkinter import *
from io import BytesIO
from PIL import Image, ImageTk
import requests
import xmltodict
from bs4 import BeautifulSoup as bs

"""
TODO:
[X] make cases for mono types and abilities
[ ] align things in GUI better
[ ] get pokemon name as title of window
[ ] make a scrollable list and a search function to browse through pokemon
[ ] add regional forms, somehow
"""

url = "https://pokemondb.net/static/sitemaps/pokemondb.xml"
pkmnPage = "pkmnPageREAL.json"
pkmnInfo = "pkmnInfoREAL.json"

# url = "https://is.gd/5xpaki"
# pkmnPage = "pkmnPageTEST.json"
# pkmnInfo = "pkmnInfoTEST.json"

root = Tk()

# global variables
reggie = "https\\:\\/\\/pokemondb\\.net\\/pokedex\\/(?!game|stats).*"
keyArray = ["natNo", "types", "species", "height", "weight", "abilities"]


def getPkmnPageList():
    # initialize pkmnPageList to hold all the links
    pkmnPageList = []
    filePath = Path(pkmnPage)

    if os.path.exists(filePath):
        print("File found! Starting to scrape each indiviual page for info...")
        with open(filePath, 'r', encoding='utf-8') as file:
            pkmnPageList = json.load(file)

    else:
        print("File not found. Starting to scrape to get the link to each pokémon's page...")
        page = requests.get(url)

        # this gets the XML file
        data = page.content

        # make it a dict
        dataDict = xmltodict.parse(data)

        for i in dataDict['urlset']['url']:
            if ('priority' in i):
                if re.search(reggie, i.get('loc')):
                    pkmnPageList.append(i)

        json_object = json.dumps(pkmnPageList, indent=4)

        with open(pkmnPage, "w+", encoding="utf-8") as outfile:
            outfile.write(json_object)

        print("Ok, we made it. Don't lose it now!")

    return pkmnPageList

def getName(url):
    newPage = requests.get(url)
    soup = bs(newPage.content, "html.parser")

    # get and return pkmn name from page
    return soup.find("h1").text

def getImgLink(url):
    newPage = requests.get(url)
    soup = bs(newPage.content, "html.parser")

    # gets all images on the page and puts them into an array
    pkmnImg = soup.find_all("img")

    # we only need pkmnImg[1], at least for now
    return pkmnImg[1]['src']

def getVitalTableRows(url):
    newPage = requests.get(url)
    soup = bs(newPage.content, "html.parser")

    vitalTable = soup.find("table")

    tableRows = vitalTable.find_all("tr")

    arrayOfDicts = []

    arrayOfDicts.append({"natNo":tableRows[0].find("td")})
    arrayOfDicts.append({"types":getTypes(tableRows[1].find("td"))})
    arrayOfDicts.append({"species":tableRows[2].find("td")})
    arrayOfDicts.append({"height":tableRows[3].find("td")})
    arrayOfDicts.append({"weight":tableRows[4].find("td")})
    arrayOfDicts.append({"abilities":getAbilities(tableRows[5].find("td"))})

    # return tableRows
    return arrayOfDicts

    """
    def getNatNo(url):
    tableRows = getVitalTableRows(url)

    daNumber = tableRows[0]
    typeContainer = daNumber.find("td")
    actualType = typeContainer.find("strong")

    natNo = actualType.text

    return natNo
    """

def getTypes(tableCell):
    actualType = tableCell.find_all("a")

    typeArray = [actualType[0].text]

    if len(actualType) == 2:
        typeArray.append(actualType[1].text)
    else:
        typeArray.append("None")

    return typeArray

    """
    def getHeight(url):
    tableRows = getVitalTableRows(url)

    daNumber = tableRows[0]
    container = daNumber.find("td")

    height = container.text

    return height
    """

def getAbilities(tableCell):
    abilities = tableCell.find_all("span")
    hiddenAbility = tableCell.find_all("small")

    abilityArray = [abilities[0].find("a").text]

    if len(abilities) == 2:
        abilityArray.append(abilities[1].find("a").text)
    else:
        abilityArray.append("None")

    if len(hiddenAbility) == 0:
        daHiddenOne  = "None"
    else:
        daHiddenOne = hiddenAbility[0].find("a").text

    abiliDict = {"abilities":{"mainAbilities":abilityArray,"hiddenAbilities":daHiddenOne}}

    return abiliDict

def makePokedex():
    pokedex = {}
    filePath = Path(pkmnInfo)

    if os.path.exists(filePath):
        print("File found! Using that to generate GUI...")
        with open(filePath, 'r', encoding='utf-8') as file:
            pokedex = json.load(file)
    else:
        # gets the info for each pokemon and stores each entry into a dict
        for pkmnPage in pkmnPageList:
            # gets the link to the pokemon's page
            newURL = pkmnPage['loc']
            pkmnName = getName(newURL)

            # array of dicts
            dictArray = getVitalTableRows(newURL)

            # initialize entry with image link
            pkmnEntry = {pkmnName:{'img':getImgLink(newURL)}}

            # puts various info into dict
            for index, key in zip(range(len(dictArray)), keyArray):
                if key == "types":
                    pkmnEntry[pkmnName].update({key:dictArray[index][key]})
                elif key == "abilities":
                    pkmnEntry[pkmnName].update(dictArray[index][key])
                else:
                    pkmnEntry[pkmnName].update({key:dictArray[index][key].text})

            # updates actual "pokédex" pokémon entry 
            pokedex.update(pkmnEntry)

    return pokedex

def formatMono(array):
    if array[1] == "None":
        return array[0]
    return (f"{array[0]}/{array[1]}")

def urlToImage(url):
    response = requests.get(url)
    img_data = response.content
    img = Image.open(BytesIO(img_data))
    # Convert the image to a format Tkinter can use
    tk_img = ImageTk.PhotoImage(img)
    return tk_img

# takes in a url as a string, returns an array
pkmnPageList = getPkmnPageList()

# makes pokedex
pokedex = makePokedex()

# array of tkinter images
masterPkmnImgs = []

# json_object = json.dumps(pkmnImg, indent=4)

# with open("pkmn.json", "w+") as outfile:
# 	outfile.write(json_object)

# i = list(pokedex.keys())

print("Enter a Pok\u00e9mon:")
balls = input()

bulbasaur = pokedex[balls]

root.title("Pok\u00e9mon")
# root.geometry("1000x600")
root.resizable(False, False)

# convert the image to a format Tkinter can use
image = urlToImage(bulbasaur["img"])

# configuration of window
root.columnconfigure(4, weight=1)
root.rowconfigure(4, weight=1)

"""
.grid(column=1, row=0)
.grid(column=0, row=1, padx=100)
.grid(column=1, row=2)
.grid()
.grid()
.grid()
.grid()
"""

Label(root, text="hi", font=("Ubuntu", 24)).pack()
Label(root, image=image, compound="left").pack()
Label(root, text=(f"National \u2116: {bulbasaur["natNo"]}"), font="Ubuntu").pack()
Label(root, text=("Type: " + formatMono(bulbasaur["types"])), font="Ubuntu").pack()
Label(root, text=("Species: " + bulbasaur["species"]), font="Ubuntu").pack()
Label(root, text=("Height: " + bulbasaur["height"]), font="Ubuntu").pack()
Label(root, text=("Weight: " + bulbasaur["weight"]), font="Ubuntu").pack()
Label(root, text=("Abilities: " + formatMono(bulbasaur["abilities"]["mainAbilities"]) + "\nHidden Ability: " + bulbasaur["abilities"]["hiddenAbilities"]), font="Ubuntu").pack()

# for names, imgs in zip()
root.mainloop()

# written to a json for easier viewing
json_object = json.dumps(pokedex, indent=4)

with open(pkmnInfo, "w+", encoding="utf-8") as outfile:
	outfile.write(json_object)

print("Done!")