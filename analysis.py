import datetime
import json
from database_connector import getFullDumpJSON

def isDayEqual(a, b):
    '''
    Takes two datetime objects and compares their date
    '''
    if type(a) == datetime.datetime and type(b) == datetime.datetime:
        return a.date() == b.date()
    else:
        raise ValueError("provide a valid datetime object! You provided", type(a),"and",type(b) )

def getAllEntriesOfDay(day, userid = None):
    db_content = getFullDumpJSON() # read DB

    # filter for date
    entriesOfDay = [item for item in db_content if isDayEqual(datetime.datetime.fromisoformat(item["timestamp"]), day)]

    # only get latest entry per each user
    users_present = {}
    for item in entriesOfDay:
        user = item["userid"]
        if userid and user != userid:
            continue # when we are looking for a specific user, skip all others

        if user in users_present:
            # duplicate entry of user
            olddate = datetime.datetime.fromisoformat(users_present[user]["timestamp"])
            newdate = datetime.datetime.fromisoformat(item["timestamp"])

            if newdate < olddate:
                # present entry is more recent
                # equal timestamps get overwritten by later occurence!
                continue
            
        # else we found a more recent entry or new user
        users_present[user] = item
    
    # remove duplicates
    entriesOfDay = list(users_present.values())

    return entriesOfDay

def getAllEntriesOfDayRange(day_start, day_end, userid = None):
    day = day_start
    entriesOfRange = []
    while day <= day_end:
        entriesOfDay = getAllEntriesOfDay(day, userid)
        if len(entriesOfDay) > 0:
            entriesOfRange.append(entriesOfDay)
        day += datetime.timedelta(days=1)
    return entriesOfRange

def aggregateMultiple(entries, keylist, aggregatelist):
    # entries have to be in day-bins (list of list)
    if not type(keylist) is list:
        keylist = [keylist]
    if not type(aggregatelist) is list:
        aggregatelist = [aggregatelist]

    # aggregate over days
    timeline = [] # list of dict with {timestamp:, data:,...}    
    for day in entries:
        valueslist = {}
        if len(aggregatelist) == 1:
            # only one aggregate given for all keys
            aggregatelist = [aggregatelist[0]]*len(keylist)
        elif len(aggregatelist) != len (keylist):
            raise ValueError("number of keys and aggregates does not match! #keys:",len(keylist),"#aggregates:",len(aggregatelist))

        for key, aggregate_type in zip(keylist,aggregatelist):
            if key+"_"+aggregate_type in valueslist:
                raise ValueError("duplicate key-aggregate pair! key:",key,"aggregate:",aggregate_type)
            if aggregate_type == "average":
                # average all values of day and key
                average = 0
                count_valid_entries = 0
                for entry in day:
                    data = json.loads(entry["data"])
                    if key in data:
                        try:
                            number = float(data[key]) # no NoneType no str, ...
                        except (ValueError, TypeError):
                            continue
                        average += number
                        count_valid_entries += 1
                        if count_valid_entries != 0:
                            average /= count_valid_entries
                valueslist[key+"_"+aggregate_type] = average
            elif aggregate_type == "max":
                returnVal = None
                entries = [json.loads(entry["data"]) for entry in day]
                values = [tryParse(float,entry[key]) for entry in entries if key in entry and not tryParse(float,entry[key]) is None]
                values = [x for x in values if x is not None]
                if len(values) > 0:
                    returnVal = max(values)
                valueslist[key+"_"+aggregate_type] = returnVal
            elif aggregate_type == "min":
                returnVal = None
                entries = [json.loads(entry["data"]) for entry in day]
                values = [tryParse(float,entry[key]) for entry in entries if key in entry and not tryParse(float,entry[key]) is None]
                if len(values) > 0:
                    returnVal = min(values)
                valueslist[key+"_"+aggregate_type] = returnVal
            elif aggregate_type == "all":
                entries = [json.loads(entry["data"]) for entry in day]
                values = [tryParse(float,entry[key]) for entry in entries if key in entry]
                valueslist[key+"_"+aggregate_type] = values
            else:
                valueslist[key+"_"+aggregate_type] = None
                raise ValueError("aggregate type",aggregate_type,"is not defined!")
    
        timeline.append({
            "timestamp": datetime.datetime.fromisoformat(day[0]["timestamp"]).date().isoformat(), # strip away the time from timestamp
            "values": valueslist
        })
    timeline.sort(key=lambda item:item["timestamp"]) # make sure the return list is sorted by timestamp
    return timeline

def tryParse(typeq,value):
    print("cal",value)
    if value is None:
        return None
    try:
        print(value)
        return typeq(value)
    except ValueError:
        return None

def padMissingDays(entries):
    if len(entries) < 2:
        return entries

    empty_values = {}
    for k in entries[0]["values"].keys():
        if type(entries[0]["values"][k]) is list:
            empty_values[k] = [None]
        else:
            empty_values[k] = None
    day =  datetime.datetime.fromisoformat(entries[0]["timestamp"])
    padded_entries = []
    counter = 0
    while day <= datetime.datetime.fromisoformat(entries[-1]["timestamp"]):
        if datetime.datetime.fromisoformat(entries[counter]["timestamp"]).date() == day.date():
            padded_entries.append(entries[counter]) # copy present data
            counter += 1
        else:
            # put in some padding
            padded_entries.append( { 
                "timestamp" : day.date().isoformat(), 
                "values" : empty_values 
            } )
        day += datetime.timedelta(days=1)

    return padded_entries