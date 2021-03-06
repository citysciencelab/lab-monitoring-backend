import csv
import random
import json
import datetime

def getUserId(username):
    dbentry = readCSVbyKey("users_db.csv", username)
    if not dbentry or len(dbentry) < 2:
        raise ValueError("this user was not found!")
    return dbentry[1]

def getUserData(username):
    dbentry = readCSVbyKey("users_db.csv", username)
    if not dbentry:# or len(dbentry) < 3:
        raise ValueError("this user was not found or has no data!")
    if len(dbentry) < 3:
        return {}
    return json.loads(dbentry[2])

def generateID():
    hash = random.getrandbits(128)
    # print("hash value: %032x" % hash)
    return hash

def setUserData(userid, userdata):
    if checkUser(userid): # user exists
        del userdata["username"] # anonymisation :P

        # delete all empty and null values from userdata
        userdata = {k: v for k, v in userdata.items() if v is not None and v is not ""}

        file = "users_db.csv"
        rows = []
        username = ""
        with open(file, 'r') as csvfile:
            reader = csv.reader(csvfile, delimiter=',', quotechar='\'') # use ' as quotechar, since json string representation uses "
            for row in reader:
                if row[1] != userid:
                    rows.append(row)
                else: # this row will be overwritten
                    username = row[0]
        with open(file, 'w', newline='') as csvfile: # newline '' prohibits stupid windows CR
            csvwriter = csv.writer(csvfile, delimiter=',', quotechar='\'', quoting=csv.QUOTE_MINIMAL) # use ' as quotechar, since json string representation uses "
            csvwriter.writerows(rows)
            csvwriter.writerow([username,userid,json.dumps(userdata)])

    else:
        raise ValueError("this user id was not found!")

def makeUser(username, userdata = None):
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

        timestamp = getTimeStamp()
        if data.get("yesterday"): # someone forgot, huh?
            # set to latest second of yesterday, so this will be the most recent entry of yesterday
            timestamp -= datetime.timedelta(days=1)
            timestamp = timestamp.replace(hour=23,minute=59,second=59,microsecond=999999)
        newEntry = [numLines, timestamp, userid, json.dumps(data) ]
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
    return output
