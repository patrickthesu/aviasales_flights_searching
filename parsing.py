from datetime import datetime, timedelta
import requests
import hashlib

import config

URL = "http://api.travelpayouts.com/v1/flight_search"
#https://www.aviasales.ru/search/MOW2705ABA1
#MOW1205ABA1

print (datetime.now())

cities = {
        "москва": "MOW",
        "абакан": "ABA",
        }

def getAirportCode (name):
    return cities[name.lower().strip()] 

tripClasses = {"Эконом": "Y", "Бизнес": "C"}
passengers = {
        "adults": 0,
        "children": 0,
        "infants": 0,
        }

#date

# ВашТокен:beta.aviasales.ru:ru:ВашМаркер:1:0:0:2021-12-25:NYC:LAX:2021-12-30:LAX:NYC:Y:127.0.0.1 

def getStrDate (date):
    return date.strftime("%Y-%m-%d")

def makeStrSegment (date = datetime.now(), origin = "MOS", destination = "ABA"):
    return f"{getStrDate(date)}:{origin}:{destination}:"

def makeJsonSegments (*args):
    outJson = [{}]  
    args = args[0]
    for arg in args:
        print (type(arg))
        if type (arg) == datetime: outJson[len(outJson)-1]["date"] = getStrDate(arg)
        elif not "origin" in outJson[len(outJson)-1]: outJson[len(outJson)-1]["origin"] = arg            
        elif not "destination" in outJson[len(outJson)-1]: outJson[len(outJson)-1]["destination"] = arg
        else: outJson += {}
    return outJson


def convertToMd5 (text):
    return hashlib.md5(text).hexdigest()

def getSignature (passengers, tripClass = list(tripClasses.values())[0], *racesdata):
    passengers = list(passengers.values())
    preEncryption = f"{config.token}:beta.aviasales.ru:{config.locale}:{config.marker}:{passengers[0]}:{passengers[1]}:{passengers[2]}:"
    for racedata in racesdata: preEncryption += makeStrSegment (*racedata)
    preEncryption += f"{tripClass}:{config.userIp}"
    print (preEncryption)
    return convertToMd5 (bytes(preEncryption, "utf-8"))

def getJsonRequest (passengers, tripClass = list(tripClasses.values())[0], *racesdata, **kwargs):
    jsonRequest = {
            "signature": (getSignature (passengers, tripClass, *racesdata)),
            "marker": config.marker,
            "host": config.host,
            "user_ip": config.userIp,
            "locale": config.locale,
            "trip_class": tripClass,
            "passengers": passengers,
            "segments": makeJsonSegments (*racesdata)
            }
    print (jsonRequest)
    return jsonRequest

def generateUrl (dep = "", arr = "", date = "2705", persons = 1, ):
    urlResponse = URL + f"{dep}{date}{arr}{persons}"
    print (urlResponse)
    return urlResponse 

def requestFlights (jsonData):
    response = requests.post(URL, json = jsonData)
    return response.text

def getPage (url):
    session = requests.session ()
    response =  session.post (url)

    return response.text

def getCode (text):
    text = text.replace (" ", "%")
    print (text)
    resp = requests.get (f"https://www.travelpayouts.com/widgets_suggest_params?q={text}")
    print (resp.text)
    return resp.json()

def get_price(date, origin, destination):
    date = getStrDate (date)
    resp = requests.get(f'https://api.travelpayouts.com/aviasales/v3/prices_for_dates?currency=rub&origin={origin}&destination={destination}&departure_at={date}&token={config.token}')
    
    if resp.status_code != 200:
        print(resp.status_code)
        print(resp.text)
        print('ПАМАГИТЕ')
    
    if not resp.json()['data']:
        return 0
    return resp.json()['data'][0]['price']
#to parse md5
#https://miraclesalad.com/webtools/md5.php

if __name__ == "__main__":
    #print (getCode (input ()))
    #print (get_price (datetime.now() + timedelta(days=-1), "SVO", "ABA"))
    newpassengers = passengers.copy()
    newpassengers["adults"] = 1
    #print (getSignature (newpassengers, list(tripClasses.values())[0], [datetime.now() + timedelta(days=5), "MOS", "ABA"]))
    #print (getJsonRequest (newpassengers, list(tripClasses.values())[0], [datetime.now() + timedelta(days=5), "MOS", "ABA"])) 
    print (requestFlights (getJsonRequest (newpassengers, list(tripClasses.values())[0], [datetime.now() + timedelta(days=1), "SVO", "ABA"],[datetime.now() + timedelta(days=3), "ABA", "SVO"])))
    #with open ("response.html", "w") as file:
        #file.write (getPage (generateUrl(getAirportCode(input("DEP:")), getAirportCode(input("ARR:")))))

