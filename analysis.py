import datetime

from database_connector import getFullDumpJSON

def isDayEqual(a, b):
    '''
    Takes two datetime objects and compares their date
    '''
    if type(a) == datetime.datetime and type(b) == datetime.datetime:
        return a.date() == b.date()
    else:
        raise ValueError("provide a valid datetime object! You provided", type(a),"and",type(b) )

def getAllEntriesOfDay(day):
    db_content = getFullDumpJSON() # read DB

    # filter for date
    entriesOfDay = [item for item in db_content if isDayEqual(datetime.datetime.fromisoformat(item["timestamp"]), day)]

    # only get latest entry per each user
    users_present = {}
    for item in entriesOfDay:
        user = item["userid"]
        if user in users_present:
            # duplicate entry of user
            olddate = datetime.datetime.fromisoformat(users_present[user]["timestamp"])
            newdate = datetime.datetime.fromisoformat(item["timestamp"])

            if newdate < olddate:
                # present entry is more recent
                continue
            
        # else we found a more recent entry or new user
        users_present[user] = item
    
    # remove duplicates
    entriesOfDay = list(users_present.values())

    return entriesOfDay

def getAllEntriesOfDayRange(day_start, day_end):
    day = day_start
    entriesOfRange = []
    while day <= day_end:
        entriesOfDay = getAllEntriesOfDay(day)
        if len(entriesOfDay) > 0:
            entriesOfRange.append(entriesOfDay)
        day += datetime.timedelta(days=1)
    return entriesOfRange