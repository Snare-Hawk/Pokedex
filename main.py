import fileinput
import json
import os
import re
from pathlib import Path

import requests
import xmltodict
from bs4 import BeautifulSoup as bs

"""
from tkinter import *
from io import BytesIO
from PIL import Image, ImageTk

root = Tk()
"""

# global variables
reggie = "https\\:\\/\\/pokemondb\\.net\\/pokedex\\/(?!game|stats).*"
keyArray = ["natNo", "types", "species", "height", "weight", "abilities"]


def getPkmnPageList(url):
    # initialize pkmnPageList to hold all the links
    pkmnPageList = []
    filePath = Path("pkmnPagesTEST.json")

    if os.path.exists(filePath):
        with open(filePath, 'r', encoding='utf-8') as file:
            pkmnPageList = json.load(file)

    else:
        print("File was not found. Starting to scrape...")
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

        with open("pkmnPagesTEST.json", "w+", encoding="utf-8") as outfile:
            outfile.write(json_object)
        
        print("Ok, we made it. Don't lose it.")

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
    arrayOfDicts.append({"abilities":tableRows[5].find("td")})

    # return tableRows
    return arrayOfDicts

def getNatNo(url):
    tableRows = getVitalTableRows(url)

    daNumber = tableRows[0]
    typeContainer = daNumber.find("td")
    actualType = typeContainer.find("strong")
    
    natNo = actualType.text

    return natNo

def getTypes(tableCell):
    actualType = tableCell.find_all("a")
    
    typeArray = [actualType[0].text]

    if len(actualType) == 2:
        typeArray.append(actualType[1].text)
    elif len(actualType) == 1:
        typeArray.append("None")

    return typeArray

def getHeight(url):
    tableRows = getVitalTableRows(url)

    daNumber = tableRows[0]
    container = daNumber.find("td")
    
    height = container.text

    return height


def urlToImage(url):
    response = requests.get(url)
    img_data = response.content
    img = Image.open(BytesIO(img_data))
    # Convert the image to a format Tkinter can use
    tk_img = ImageTk.PhotoImage(img)
    return tk_img


# takes in a url as a string, returns an array
# url = "https://pokemondb.net/static/sitemaps/pokemondb.xml"
url = "https://cdn.discordapp.com/attachments/666436193898201109/1244159668591267920/balls.xml?ex=6654197c&is=6652c7fc&hm=be8f1422e1d2c56719e9665b3e109338cafecb090a13f4f774edf03e96d93605&"
pkmnPageList = getPkmnPageList(url)

# array of tkinter images
masterPkmnImgs = []

dictDict = {}

# with open("Output.txt", "w", encoding="utf-8") as text_file:
#     text_file.write(whatStr)

# gets the info for each pokemon and stores each entry into a dict
for pkmnPage in pkmnPageList: 
    # gets the link to the pokemon's page 
    newURL = pkmnPage['loc']
    pkmnName = getName(newURL)
    # puts various info into dict
    # dictItem = {pkmnName:{"img":getImgLink(newURL), "natNo":getNatNo(newURL),"types":getTypes(newURL)}}

    # """

    # array of dicts
    dictArray = getVitalTableRows(newURL)   

    # print(type(dictItem[pkmnName]))
    # for i in range(5):
    #     dictItem.update(dictArray[i].text)
    # """

    dictItem = {pkmnName:{'img':getImgLink(newURL)}}

    for index, key in zip(range(len(dictArray)), keyArray):
        if key == "types":
            dictItem[pkmnName].update({key:dictArray[index][key]})
        else:
            dictItem[pkmnName].update({key:dictArray[index][key].text})

    # dictItem = {
    #     pkmnName:{
    #         "img":getImgLink(newURL),
    #         'natNo':dictArray[0]['natNo'].text,
    #         # remember to include the types!
    #         'species':dictArray[1]['species'].text,
    #         'height':dictArray[2]['height'].text,
    #         'weight':dictArray[3]['weight'].text,
    #         'abilities':dictArray[4]['abilities'].text
    #         }
    #     }

    dictDict.update(dictItem)


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
json_object = json.dumps(dictDict, indent=4)

with open("PKMNinfo.json", "w+", encoding="utf-8") as outfile:
	outfile.write(json_object)

print("Done!")