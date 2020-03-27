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

def aggregateEntries(entries, key, aggregate_type):
    # entries have to be in day-bins (list of list)
    import json    
    if aggregate_type == "average":
        # aggregate over days
        timeline = [] # list of dict with {timestamp:, data:,...}

        for day in entries:
            # average all values of key
            average = 0
            count = 0
            for entry in day:
                print("entry",type(entry),entry)
                data = json.loads(entry["data"])
                print("data",type(data),data)
                if key in data and (type(data[key])==int or type(data[key])==float): # no NoneType no str, ...
                    average += data[key]
                    count += 1
            if count != 0:
                average /= count

            timeline.append({
                "timestamp": datetime.datetime.fromisoformat(day[0]["timestamp"]).date().isoformat(),
                "value": average,
                "key" : key,
                "aggregate" : aggregate_type
            })
        timeline.sort(key=lambda item:item["timestamp"]) # make sure the return list is sorted by timestamp
        return timeline

    else:
        raise ValueError("aggregate type",aggregate_type,"is not defined!")