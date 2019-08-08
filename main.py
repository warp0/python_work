import sys
from datetime import datetime, date, time
import requests
import sqlite3
import re
import pickle
import sqlalchemy

#defining classes
class tags:
    number = str
    timestamp = str
    url = str
    dictionary = str

class queries:
    tagcounterGet = str
    tagcounterPut = str

#path to database    
dbconnect=sqlite3.connect("./tagcounter.db")
cursor = dbconnect.cursor()

#defininig functions
def initDB():
    prompt = "Do you want to init databases?(Yes/No)"
    proceed = input(prompt)

    if proceed == "Yes":
        cursor.execute("""CREATE TABLE tagcounter(
            URL         TEXT    NOT NULL,
            TAGS        INT     NOT NULL,
            TIMESTAMP   TEXT    NOT NULL,
            DICTIONARY  BLOB    NOT NULL
        );"""
        )

        dbconnect.commit()
    else:
        print("No db will be created")

def recordDB(tags):
    #query
    queries.tagcounterGet="""INSERT INTO 'tagcounter'
    (URL, TAGS, TIMESTAMP, DICTIONARY) VALUES (?, ?, ?, ?);"""
    db_dictionary=pickle.dumps(tags.dictionary, protocol=pickle.HIGHEST_PROTOCOL)
    binTags=(tags.url, tags.number, tags.timestamp, db_dictionary)
    cursor.execute(queries.tagcounterGet, binTags)
    dbconnect.commit()

#counting tags number on page: CONSUMING URL, RETURNING TAGS OBJECT
def getcount(url):
    response=requests.get(url)

    tags.number = response.text.count("<")
    tags.timestamp = timestamp.strftime("%m/%d/%Y, %H:%M:%S")
    tags.url = url

    dictionary=re.findall('<\s*[a-z, A-Z]*[\s>]', response.text)
    tags.dictionary=[]
    for i in dictionary:
        i=i.replace('<','')
        i=i.replace('>','')
        i=i.replace(' ','')
        if len(i) > 0:
            tags.dictionary.append(i)
        else: 
            print("found empty tag")
    tags.dictionary=list(dict.fromkeys(tags.dictionary))

def getQuery(url):
    queries.tagcounterPut="""SELECT * FROM tagcounter where URL=?"""
    for row in cursor.execute(queries.tagcounterPut, (url,)):
        print(row[0:3], pickle.loads(row[3]))

#getting args and defining url
url=""
args_number=len(sys.argv)

if sys.argv[1]=="--get":
    initDB()
    for i in range(2,args_number):

        timestamp=datetime.now()
        url=sys.argv[i]

        if url=="ggl": 
            getcount("https://www.google.com")

        elif url=="msn": 
            getcount("https://www.msn.com")

        elif url[0:1]=="-":
            print("Err:too many commands or wrong argument expression!")
            break

        else: 
            getcount(url)
         
        #print objects
        print(tags.url, tags.number, tags.timestamp)
        print(tags.dictionary)
        print(len(tags.dictionary))

        recordDB(tags)

elif sys.argv[1]=="--view":
    
    for i in range(2,args_number):
       
        url=sys.argv[i]

        if url=="ggl": 
            getQuery("https://www.google.com")

        elif url=="msn": 
            getQuery("https://www.msn.com")

        elif url[0:1]=="-":
            print("Err:too many commands or wrong argument expression!")
            break
        else:
            getQuery(url)


#if no --command found                
else: 
    print("No command passed")

