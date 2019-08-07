import sys
from datetime import datetime, date, time
import requests
import sqlite3

#db actions
dbconnect=sqlite3.connect("Desktop/tagcounter/tagcounter.db")
cursor = dbconnect.cursor()


#cursor.execute("""CREATE TABLE tagcounter(
#    URL         TEXT    NOT NULL,
#    TAGS        INT     NOT NULL,
#    TIMESTAMP   TEXT    NOT NULL
#);"""
#)

dbconnect.commit()

url="test"
args_number=len(sys.argv)

class tags:
    number = str
    timestamp = str
    url = str


#forming tag vocabulary    
def tagDiscover(response):
    input()


def getcount(url):
    response=requests.get(url)

    tags.number = response.text.count("<")
    tags.timestamp = timestamp.strftime("%m/%d/%Y, %H:%M:%S")
    tags.url = url

   

if sys.argv[1]=="--get":
    for i in range(2,args_number):
        timestamp=datetime.now()
        url=sys.argv[i]
        if url=="ggl": getcount("https://www.google.com")
        elif url=="msn": getcount("https://www.msn.com")
        else: getcount(url)
        print(tags.url, tags.number, tags.timestamp)
        query="INSERT INTO tagcounter VALUES ('" + tags.url + "', '" + str(tags.number) + "', '" + tags.timestamp + "')"
        cursor.execute(query)
        dbconnect.commit()
        print(query)
else: print("No command passed")

