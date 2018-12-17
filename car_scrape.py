import pandas as pd
from urllib.request import Request, urlopen
from bs4 import BeautifulSoup
from pprint import pprint as pp
import re
import os
import json

link = 'https://www.kudosprime.com/gts/carlist.php?start='
filePath = '/home/adempus/Documents/Jupyter_Notebooks/GTSport_Jupyter_Sketch/cardata.json'
heads = {'Accept': 'text/html', 'User-Agent': 'Mozilla/5.0'}

def reqHtml(url, headers=heads):
    req = Request(url, headers=heads)
    webpage = urlopen(req)
    beauSoup = BeautifulSoup(webpage)  
    return beauSoup

def getCarList(index):
    heads = {'Accept': 'text/html', 'User-Agent': 'Mozilla/5.0'}
    page = reqHtml(link+str(index))
    return page.find_all('div', {'id': {'carlist'}})
    
def getCarNames(carList):
    return [c.get_text().strip() for c in carList[0].find_all(class_='name')]

def getCarCty(carList):
    return [c.get_text().strip() for c in carList[0].find_all(class_='cty')]

def getCarDrivetrain(carList):
    return [c.get_text().strip() for c in carList[0].find_all(class_='tr')]

def getCarTpw(carList):
    twpList = [str(c.get_text()).strip() for c in carList[0].find_all(class_='tpw')]
    data = {"hp": [], "lbs": []}
    for twp in twpList:
        twpData = re.split('[a-zA-Z]', twp) # all we want are numeric data values
        hp, lbs = list(filter(lambda x: x is not "", twpData))[0:2]
        data['hp'].append(hp.strip())
        data['lbs'].append(lbs.strip())
    return data

def getCarStats(carList):
    getVal = lambda attr: [c.get_text().strip() for c in carList[0].find_all(class_=attr)]
    stats = {
        'speed': getVal('sp'), 'acceleration': getVal('ac'), 'breaking': getVal('br'),
        'cornering': getVal('ha'), 'stability':  getVal('la'), 'rating': getVal('av')
    }
    return stats

def getCarData(index):
    carList = getCarList(index)
    return {
        'names': getCarNames(carList), 'categories': getCarCty(carList), 
        'drivetrains': getCarDrivetrain(carList), 'tpws': getCarTpw(carList),
        'stats': getCarStats(carList)
    }
    
def initScrape():
    results = {}
    car = lambda n, c, d, h, l, s: {
        'name': n, 'category': c, 'drivetrain': d, 'hp': h, 'lbs': l, 'stats': s 
    }
    index, pageNo = 0, 0
    while index <= 250:
        carData = getCarData(index)
        results[pageNo] = car(
            carData['names'], carData['categories'], carData['drivetrains'],
            carData['tpws']['hp'], carData['tpws']['lbs'], carData['stats']
        )
        index += 50 
        pageNo += 1
    return results
         
def writeFile(data, path):
    with open(path, 'w') as jsonFile:
        content = json.dumps(data)
        print(content, file=jsonFile)

def readFile(path):
    with open(path, 'r') as jsonFile:
        content = json.load(jsonFile)
        return content
    
if '__main__' == __name__:
    cars = None
    if os.stat(filePath).st_size == 0:
        print("File contents empty, initializing web scrape...")
        cars = initScrape()
        print("Saving file ...")
        writeFile(cars, filePath)
        print(readFile(filePath))
    else:
        print("Cars initialized from json file.")
        content = readFile(filePath)
        pp(content, indent=1)

# a pandas dataframe is a tabular (2D) representation of data in pandas
# df = pd.DataFrame()
