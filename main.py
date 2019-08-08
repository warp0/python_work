import sys
from datetime import datetime, date, time
import requests
import sqlite3
import re
import pickle
from collections import Counter 
import json

#defining classes
class tags:
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
            TIMESTAMP   TEXT    NOT NULL,
            DICTIONARY  BLOB    NOT NULL
        );"""
        )

        dbconnect.commit()
    else:
        print("No db will be created")

def recordDB(tags):
    #query
    queries.tagcounterPut="""INSERT INTO 'tagcounter'
    (URL, TIMESTAMP, DICTIONARY) VALUES (?, ?, ?);"""
    db_dictionary=pickle.dumps(tags.dictionary, protocol=pickle.HIGHEST_PROTOCOL)
    binTags=(tags.url, tags.timestamp, db_dictionary)
    cursor.execute(queries.tagcounterPut, binTags)
    dbconnect.commit()

def getquery(url):
    queries.tagcounterGet="""SELECT * FROM 'tagcounter' WHERE URL=?"""
    for row in cursor.execute(queries.tagcounterGet, (url,)):
        print(row[0:2], pickle.loads(row[2]))

#counting tags number on page: CONSUMING URL, RETURNING TAGS OBJECT
def getcount(url):
    response=requests.get(url)

    tags.timestamp = timestamp.strftime("%m/%d/%Y, %H:%M:%S")
    tags.url = url

    #working with dictionary
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
    tags.dictionary=Counter(tags.dictionary)
    
    #logging
    log_obj = {
        'time': tags.timestamp,
        'url' : tags.url
    }
    with open('./parsed.log','a') as logfile:
        json.dump(log_obj, logfile)
        logfile.write("\n")


#getting args and defining url
url=""
args_number=len(sys.argv)

if sys.argv[1]=="--get":
    initDB()
    for index1 in range(2,args_number):
        #check for correct syntax
        if url[0:1]=="-":
            print("Err:too many commands or wrong argument expression!")
            break
        
        #reset alias_checker
        alias_checker=0
        
        #check for time and set url from args
        timestamp=datetime.now()
        url=sys.argv[index1]
        
        #read aliases
        with open("./aliases.cfg", "r") as alias_file:
            alias_map=json.load(alias_file)
        for alias in alias_map:  
            if alias==url:
                getcount(alias_map[alias])
                alias_checker=alias_checker + 1
                print("alias found")
        
        #if alias check failed - we have valid url:
        if alias_checker < 1:
            getcount(url)
         
        #print obtained data
        print(tags.url, tags.timestamp)
        print(tags.dictionary)
        print(len(tags.dictionary))
        
        #record object to database
        recordDB(tags)

elif sys.argv[1]=="--view":
    for index2 in range(2,args_number):
        alias_checker=0
        url=sys.argv[index2]
        
        with open("./aliases.cfg", "r") as alias_file:
            alias_map=json.load(alias_file)
        
        for alias in alias_map:  
            if alias==url:
                getquery(alias_map[alias])
                alias_checker=alias_checker + 1
                print("alias found")

        #if alias check not incremented - we have non-alias url:
        if alias_checker < 1:
            getquery(url)
        

#if no --command found                
else: 
    print("No command passed")

