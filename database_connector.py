import csv
import random


def getUserId(username):
    dbentry = readCSVbyKey("users_db.csv", username)
    if not dbentry or len(dbentry) < 2:
        raise ValueError("this user was not found!")
    return dbentry[1]

def generateID():
    hash = random.getrandbits(128)
    print("hash value: %032x" % hash)
    return hash

def makeUser(username):
    file = "users_db.csv"
    with open(file, 'a', newline='') as csvfile:
        csvwriter = csv.writer(csvfile, delimiter=',',
                                quotechar='"', quoting=csv.QUOTE_MINIMAL)

        userid = generateID()
        while(checkUser(userid)): # id already exists (what a chance!)
            userid = generateID() # generate a new one
                    
        newEntry = [username, userid]
        csvwriter.writerow(newEntry)
    return userid


def readCSVbyKey(file, key):
    with open(file, 'r') as csvfile:
        lines = csv.reader(csvfile, delimiter=',', quotechar='"')
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
        numLines = len(list(lines))

    with open(file, 'a', newline='') as csvfile:
        csvwriter = csv.writer(csvfile, delimiter=',',
                                quotechar='"', quoting=csv.QUOTE_MINIMAL)
        newEntry = [numLines, getTimeStamp(), userid]+data
        print(newEntry)
        csvwriter.writerow(newEntry)