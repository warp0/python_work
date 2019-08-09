import sys
from datetime import datetime, date, time
import requests
import sqlite3
import re
import pickle
from collections import Counter 
import json


from tkinter import *
from tkinter import messagebox
from tkinter.ttk import *

#initial
cl_args=[]
dbconnect=sqlite3.connect("./tagcounter.db")
cursor = dbconnect.cursor()
global var_UI
var_UI = False

#defining interface
def ui():
    def btn_exec():
        global var_init_DB
        cl_args.append("main.py")
        cl_args.append(radio_selection.get())
        if len(combo.get()) > 1:
            cl_args.append(combo.get())
        if len(txt1.get()) > 1:
            cl_args.append(txt1.get())
        if len(txt2.get()) > 1:
            cl_args.append(txt2.get())
        if len(txt3.get()) > 1:
            cl_args.append(txt3.get())
        if len(txt4.get()) > 1:
            cl_args.append(txt4.get())
        if len(txt5.get()) > 1:
            cl_args.append(txt5.get())
        var_init_DB = checkbox_var.get()
        main()
        cl_args.clear()
    
    window = Tk()
    window.title("Tag counter")
    window.geometry('625x575')

    lbl = Label(window, text="Tag counter", font=("Arial Bold", 20))
    lbl.grid(column=0, row=0)

    lbl2 = Label(window, text="Select site to parse from cfg file, or write your own", font=("Terminal", 10))
    lbl2.grid(column=0, row=1)

    radio_selection = StringVar()
    checkbox_var = BooleanVar()
    
    #Look what's in aliases
    with open("./aliases.cfg", "r") as alias_file:
        alias_map=json.load(alias_file)
    alias_site_list=[]
    for alias in alias_map:
        alias_site_list.append(alias_map[alias])

    #create combobox
    combo = Combobox(window, values=alias_site_list)
    combo.grid(column=0, row=2)
    
    #radio buttons for -get or -view
    rad1 = Radiobutton(window,text='Parse sites', value="--get", variable=radio_selection)
    rad2 = Radiobutton(window,text='View parsed sites', value="--view", variable=radio_selection)

    rad1.grid(column=0, row=3)
    rad2.grid(column=0, row=4)
    
    #txt for input
    txt1 = Entry(window,width=50)
    txt1.grid(column=0, columnspan=1, row=5, pady=10, padx=10)
    txt2 = Entry(window,width=50)
    txt2.grid(column=0, columnspan=1, row=6, pady=10, padx=10)
    txt3 = Entry(window,width=50)
    txt3.grid(column=0, columnspan=1, row=7, pady=10, padx=10)
    txt4 = Entry(window,width=50)
    txt4.grid(column=0, columnspan=1, row=8, pady=10, padx=10)
    txt5 = Entry(window,width=50)
    txt5.grid(column=0, columnspan=1, row=9, pady=10, padx=10)
     
    #checkbox for init db
    checkbox = Checkbutton(window, text="Init DB", variable=checkbox_var)
    checkbox.grid(row=10, column=1, sticky=W)

    btn = Button(window, text="Execute", command=btn_exec)
    btn.grid(column=0, row=10, pady=10, padx=10)
    
    #list box for output
    global listbox
    listbox = Listbox(window, width=100)
    listbox.grid(column=0,columnspan=2, row=11)

    scrollbarv = Scrollbar(window, orient="vertical")
    scrollbarh = Scrollbar(window, orient="horizontal")
    scrollbarv.grid(row = 11, column = 2, sticky="NS")
    scrollbarh.grid(row = 12, columnspan = 4, sticky="WE")
    
    scrollbarv.config(command=listbox.yview)
    scrollbarh.config(command=listbox.xview)

    window.mainloop()
    
#defining classes
class tags:
    timestamp = str
    url = str
    dictionary = str

class queries:
    tagcounterGet = str
    tagcounterPut = str

#defininig functions
def initDB(): 
    try:
        cursor.execute("""CREATE TABLE tagcounter(
                URL         TEXT    NOT NULL,
                TIMESTAMP   TEXT    NOT NULL,
                DICTIONARY  BLOB    NOT NULL
            );"""
        )
        dbconnect.commit()
    except:
        if var_UI == True: 
            messagebox.showerror("Error", "An ERROR creating DB occured. Probably DB already exists!")
        else:
            print("An ERROR creating DB occured. Probably DB already exists!")


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
        if var_UI == True:
            listbox.insert(END, pickle.loads(row[2]))
        else:
                print(row[0:2], pickle.loads(row[2]))

#counting tags number on page: CONSUMING URL, RETURNING TAGS OBJECT
def getcount(url):
    response=requests.get(url)
    timestamp=datetime.now()
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


def main():        
    #path to database    


    #getting args and defining url
    url=""
    args_number=len(cl_args)
    
    if (var_UI==True) and (var_init_DB==True) and (cl_args[1]=="--get"):
        initDB()
    elif var_UI==False:
        prompt = "Do you want to init databases?(y/n)"
        proceed = input(prompt)
        if proceed== "y":
            print("Initializing DB...")
            initDB()

    if cl_args[1]=="--get":
        for index1 in range(2,args_number):
            
            #get URL, check for correct syntax & check for time           
            url=cl_args[index1]
            
            if url[0:1]=="-":
                print("Err:too many commands or wrong argument expression!")
                break
            
            #reset alias_checker
            alias_checker=0
            
            #read aliases
            with open("./aliases.cfg", "r") as alias_file:
                alias_map=json.load(alias_file)
            for alias in alias_map:  
                if alias==url:
                    getcount(alias_map[alias])
                    alias_checker=alias_checker + 1
                    print("alias found and processed")
            
            #if alias check failed - we have valid url:
            if alias_checker < 1:
                getcount(url)
            
            #print obtained data
            if var_UI == True:
                listbox.insert(END, tags.timestamp, tags.url, "Tags found: ", tags.dictionary, "\n" )
            else:
                print(tags.timestamp, tags.url, "Tags found: ", tags.dictionary)
            #record results to database
            recordDB(tags)

    elif cl_args[1]=="--view":
        for index2 in range(2,args_number):
            alias_checker=0
            url=cl_args[index2]
            
            with open("./aliases.cfg", "r") as alias_file:
                alias_map=json.load(alias_file)
            
            for alias in alias_map:  
                if alias==url:
                    print("alias found:", alias)
                    getquery(alias_map[alias])
                    alias_checker=alias_checker + 1
                    
            #if alias check not incremented - we have non-alias url:
            if alias_checker < 1:
                getquery(url)
            

    #if no --command received                
    else: 
        if var_UI == True: 
            messagebox.showerror("Error", "No command received")
        else:
            print("No command received")

#function to check for arguments passed in command line
if len(sys.argv) > 1:
    for arguments in sys.argv:
        cl_args.append(arguments)
    main()

    #if no args found - starting UI mode        
else:
    var_UI=True
    ui()
    
           

    #checking if no arguments were handled and exiting programm if true
if len(sys.argv)==1 and len(cl_args)<2:
    exit()

#tests
#try getcount("test non url") and catch error
#try recorddb("wrong object") and catch error
#try getquery("not url") and receive empty result
