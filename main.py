from bs4 import BeautifulSoup as bs
import requests
import json
import xmltodict
import re
from tkinter import *
from io import BytesIO
from PIL import Image, ImageTk


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

# for pkmn in masterList
newURL = masterList[0]['loc']
newPage = requests.get(newURL)

# get info from pkmn page
soup = bs(newPage.content, "html.parser")
pkmnName = soup.find("h1").text
pkmnImg = soup.find_all("img")


# json_object = json.dumps(pkmnImg, indent=4)

# with open("pkmn.json", "w+") as outfile:
# 	outfile.write(json_object)

root = Tk()
root.title(pkmnName)
root.geometry("500x500")

def urlToImage(url):
    response = requests.get(url)
    img_data = response.content
    img = Image.open(BytesIO(img_data))
    # Convert the image to a format Tkinter can use
    tk_img = ImageTk.PhotoImage(img)
    return tk_img

pkmnImg = urlToImage(pkmnImg[1]['src'])
Label(root, text="hi", font=("Ubuntu", 24)).pack()
Label(root,image=pkmnImg).pack()

root.mainloop()

# ws = Tk()  
# ws.title('PythonGuides')
# ws.geometry('500x500')

# canvas = Canvas(ws, width=4000, height=4000)  
# canvas.pack()  
# img = ImageTk.PhotoImage(Image.open())  
# canvas.create_image(40, 20, anchor=NW, image=img) 
# ws.mainloop() 



# written to a json for easier viewing
json_object = json.dumps(masterList, indent=4)

with open("jobs.json", "w+") as outfile:
	outfile.write(json_object)
