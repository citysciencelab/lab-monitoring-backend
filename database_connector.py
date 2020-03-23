import csv
import random
import json

def getUserId(username):
    dbentry = readCSVbyKey("users_db.csv", username)
    if not dbentry or len(dbentry) < 2:
        raise ValueError("this user was not found!")
    return dbentry[1]

def getUserData(username):
    dbentry = readCSVbyKey("users_db.csv", username)
    if not dbentry or len(dbentry) < 3:
        raise ValueError("this user was not found or has no data!")
    return dbentry[2]

def generateID():
    hash = random.getrandbits(128)
    print("hash value: %032x" % hash)
    return hash

def makeUser(username, userdata = {}):
    file = "users_db.csv"
    with open(file, 'a', newline='') as csvfile:
        csvwriter = csv.writer(csvfile, delimiter=',',
                                quotechar='\'', quoting=csv.QUOTE_MINIMAL) # use ' as quotechar, since json string representation uses "

        userid = generateID()
        while(checkUser(userid)): # id already exists (what a chance!)
            userid = generateID() # generate a new one
                    
        newEntry = [username, userid, json.dumps(userdata)]
        csvwriter.writerow(newEntry)
    return userid


def readCSVbyKey(file, key):
    with open(file, 'r') as csvfile:
        lines = csv.reader(csvfile, delimiter=',', quotechar='\'') # use ' as quotechar, since json string representation uses "
        for row in lines:
            if key in row:
                return row
    return None

def checkUser(userid):
    dbentry = readCSVbyKey("users_db.csv", userid)
    if not dbentry or len(dbentry) < 2:
        return False
    return dbentry[1] == userid

import datetime

def getTimeStamp():
    return datetime.datetime.today()

def appendData(userid, data):
    file = "data_db.csv"
    numLines = None
    with open(file, 'r') as csvfile:
        lines = csv.reader(csvfile, delimiter=',')
        numLines = len(list(lines)) # get the current number of entries for use as an id

    with open(file, 'a', newline='') as csvfile:
        csvwriter = csv.writer(csvfile, delimiter=',',
                                quotechar='\'', quoting=csv.QUOTE_MINIMAL) # use ' as quotechar, since json string representation uses "
        newEntry = [numLines, getTimeStamp(), userid, json.dumps(data) ]
        csvwriter.writerow(newEntry)

def getFullDumpStr():
    file = "data_db.csv"
    output = ""
    with open(file, 'r') as csvfile:
        reader = csv.reader(csvfile, delimiter=',', quotechar='\'') # use ' as quotechar, since json string representation uses "
        for line in reader:
            output += str(line) + "\n"
    return output

def getFullDumpJSON():
    file = "data_db.csv"
    output = []
    with open(file, 'r') as csvfile:
        reader = csv.DictReader(csvfile, delimiter=',', quotechar='\'') # use ' as quotechar, since json string representation uses "
        for line in reader:
            output.append(dict(line))
    print(output)
    return output
