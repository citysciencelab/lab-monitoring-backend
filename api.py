import datetime
import pygal
from flask import Flask, request, render_template, jsonify, abort
from flask_cors import CORS, cross_origin
from database_connector import getUserId, getUserData, appendData, makeUser, getFullDumpJSON, checkUser, setUserData
import analysis

app = Flask(__name__)
CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

def parseReq(request):
    if request.method == 'POST':
        params = dict(request.json)
    elif request.method == "GET":
        params = {}
        for key in request.args.keys():
            # we have to parse this element by element, to detect mduplicate keys
            if len(request.args.getlist(key)) > 1:
                params[key] = request.args.getlist(key) # duplicate key, store all values as list
            else:
                params[key] = request.args[key] # default behaviour: store single value
    else:
        abort(400)
    
    if params and len(params.items()) > 0:
        return params
    else:
        return {}

def tryParseList(data):
    # this parses lists given as strin [x,y,z] into real lists or returns None, if it wasn't a list
    if type(data) is list: # already got valid list (probably JSON via POST)
        return data
    elif type(data) is str: # got GET list or string
        if data[0] == "[": # got list in string
            data = data[1:-1] # trim brackets
            return data.split(",") # return as list
    return None # else: no list

def listToVerboseStr(wordList):
    if type(wordList) is str:
        return wordList
    if len(wordList) == 0:
        raise ValueError
    result = str(wordList[0])
    for item in wordList[1:-1]:
        result += ", " + str(item)
    if len(wordList) >= 2:
        result += " and " + str(wordList[-1])
    return result

@app.route('/test')
def test():
    params = parseReq(request)
    return jsonify(params)

@cross_origin()
@app.route('/login', methods = ['POST'])
def login():
    params = parseReq(request)
    print("req",request.json)
    print("par",params)
    username = params.get('username')
    if username == "":
        abort(400)
    try:
        userid = str(getUserId(username))
    except ValueError:
        userid = str(makeUser(username))

    if len(params) > 1:
        # we received some new userdata, store it in DB
        setUserData(userid, params)

    try:
        userdata = getUserData(username)
    except:
        abort(401)

    response = {
            "id": userid,
            "userdata": userdata
    }
    
    return jsonify(response)

@cross_origin()
@app.route('/submit', methods = ['POST'])
def submit():
    params = parseReq(request)

    userid = params.get('id')
    if not checkUser(params['id']):
        abort(401)
    
    del params["id"]
    del params["username"] # anonymise :P
    appendData(userid,params)
    return "200 - successful submit"

@app.route('/')
def index():
    return render_template('./test_form.html')

@app.route('/rawdata', methods = ['POST','GET'])
def rawdata():
    params = parseReq(request)
    day = params.get('day')
    day_start = params.get('day_start')
    day_end = params.get('day_end')

    if day:
        day = datetime.datetime.fromisoformat(day)
        return jsonify(analysis.getAllEntriesOfDay(day))

    elif day_start and day_end:
        day_start = datetime.datetime.fromisoformat(day_start)
        day_end = datetime.datetime.fromisoformat(day_end)
        return jsonify(analysis.getAllEntriesOfDayRange(day_start, day_end))
    else:
        abort(400)

@app.route('/chart_test')
def chartTest():
    graph = pygal.Line()
    graph.title = '% Change Coolness of programming languages over time.'
    graph.x_labels = ['2011','2012','2013','2014','2015','2016']
    graph.add('Python',  [15, 31, 89, 200, 356, 900])
    graph.add('JavaScript',    [15, 45, 76, 80,  60,  35])
    graph.add('C++',     [5,  51, 54, 102, 150, 201])
    graph.add('All others combined!',  [5, 15, 21, 55, 92, 105])
    graph_data = graph.render_response()
    return graph_data

@app.route('/aggregate')
def aggr():
    params = parseReq(request)
    day_start = params.get('day_start')
    day_end = params.get('day_end')
    key = params.get('key')
    aggregate = params.get('aggregate')
    if key and aggregate:
        if day_start:
            day_start = datetime.datetime.fromisoformat(day_start)
        else:
            day_start = datetime.datetime(2020,3,1)
        if day_end:
            day_end = datetime.datetime.fromisoformat(day_end)
        else:
            day_end = datetime.datetime.today()
        entries = analysis.getAllEntriesOfDayRange(day_start, day_end)
        try:
            results = analysis.aggregateMultiple(entries, key, aggregate)
            return jsonify(results)
        except ValueError as e:
            print(e)
            abort(400)
    else:
        abort(400)

@app.route('/aggregate_plot')
def aggr_plot():
    params = parseReq(request)
    day_start = params.get('day_start')
    day_end = params.get('day_end')
    key = params.get('key')
    aggregate = params.get('aggregate')

    if key and aggregate:
        if day_start:
            day_start = datetime.datetime.fromisoformat(day_start)
        else:
            day_start = datetime.datetime(2020,3,1)
        if day_end:
            day_end = datetime.datetime.fromisoformat(day_end)
        else:
            day_end = datetime.datetime.today()
        entries = analysis.getAllEntriesOfDayRange(day_start, day_end)
        try:
            results = analysis.aggregateMultiple(entries, key, aggregate)
        except ValueError as e:
            print(e)
            abort(400)

        results = analysis.padMissingDays(results)

        if aggregate == "all" and not type(key) is list:
            # make a box plot
            graph = pygal.Box(x_label_rotation=35, truncate_label=-1)
            graph.title = "distribution of " + listToVerboseStr(key) + " over time."
            graph.x_labels = [ x["timestamp"] for x in results ]
            for day in results:
                # if not day["values"][key+"_"+aggregate][0]:
                #     graph.add(day["timestamp"],None, allow_interruptions=True)
                # else:
                graph.add(day["timestamp"], day["values"][key+"_"+aggregate], allow_interruptions=True)
        elif aggregate=="all" or "all" in aggregate :
            abort(400)
        else:
            graph = pygal.Line(x_label_rotation=35, truncate_label=-1)
            graph.title = listToVerboseStr(aggregate) + " of " + listToVerboseStr(key) + " over time."
            graph.x_labels = [ x["timestamp"] for x in results ]
            
            if not type(key) is list:
                key = [key]
            if not type(aggregate) is list:
                aggregate = [aggregate]*len(key)

            for k, a in zip(key,aggregate):
                data = [ x["values"][k+"_"+a] for x in results ]
                graph.add(k+" "+a,  data, allow_interruptions=True)

        graph_data = graph.render_response()
        return graph_data
    else:
        abort(400)

@app.route('/user_timeline')
def user_timeline():
    params = parseReq(request)
    user_id = params.get("id")
    day_start = params.get('day_start')
    day_end = params.get('day_end')
    key = params.get('key')
    if user_id and key:
        if day_start:
            day_start = datetime.datetime.fromisoformat(day_start)
        else:
            day_start = datetime.datetime(2020,3,1)
        if day_end:
            day_end = datetime.datetime.fromisoformat(day_end)
        else:
            day_end = datetime.datetime.today()
        entries = analysis.getAllEntriesOfDayRange(day_start, day_end, user_id)
        try:
            results = analysis.aggregateMultiple(entries, key, "all")
            return jsonify(results)
        except ValueError as e:
            print(e)
            abort(400)
    else:
        abort(400)

@app.route('/user_plot')
def user_plot():
    params = parseReq(request)
    user_id = params.get("id")
    day_start = params.get('day_start')
    day_end = params.get('day_end')
    key = params.get('key')
    if user_id and key:
        if day_start:
            day_start = datetime.datetime.fromisoformat(day_start)
        else:
            day_start = datetime.datetime(2020,3,1)
        if day_end:
            day_end = datetime.datetime.fromisoformat(day_end)
        else:
            day_end = datetime.datetime.today()
        entries = analysis.getAllEntriesOfDayRange(day_start, day_end, user_id)
        try:
            results = analysis.aggregateMultiple(entries, key, "all")
        except ValueError as e:
            print(e)
            abort(400)

        results = analysis.padMissingDays(results)

        graph = pygal.Line(x_label_rotation=35, truncate_label=-1)
        graph.title = listToVerboseStr(key) + " of yourself over time."
        graph.x_labels = [ x["timestamp"] for x in results ]
        
        if not type(key) is list:
            key = [key]
        aggregate = ["all"]*len(key)

        for k, a in zip(key,aggregate):
            data = [ x["values"][k+"_"+a][0] for x in results if len(x["values"][k+"_"+a]) > 0]
            graph.add(k+" "+a,  data, allow_interruptions=True)

        graph_data = graph.render_response()
        return graph_data
    else:
        abort(400)

@app.route('/num_submissions')
def num_submissions():
    params = parseReq(request)
    day = params.get('day')
    day_start = params.get('day_start')
    day_end = params.get('day_end')

    if day:
        day = datetime.datetime.fromisoformat(day)
        entries = analysis.getAllEntriesOfDay(day)
    elif day_start and day_end:
        day_start = datetime.datetime.fromisoformat(day_start)
        day_end = datetime.datetime.fromisoformat(day_end)
        entries = analysis.getAllEntriesOfDayRange(day_start, day_end)
    else:
        abort(400)

    num_entries = [ {"numberOfEntries":len(day), "date":datetime.datetime.fromisoformat(day[0]["timestamp"]).date().isoformat()} for day in entries]
    return jsonify(num_entries)

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0")