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
        params = request.json
    elif request.method == "GET":
        params = request.args
    else:
        abort(400)
    
    if params and len(dict(params).items()) > 0:
        return dict(params)
    else:
        return {}

def tryParseList(data):
    if type(data) is list: # got valid JSON via POST
        return data
    elif type(data) is str: # got GET list or string
        if data[0] == "[": # got list in string
            data = data[1:-1] # trim brackets
            return data.split(",") # return as list
    return None # else: no list

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
    return jsonify(getFullDumpJSON())

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
    if day_start and day_end and key and aggregate:
        day_start = datetime.datetime.fromisoformat(day_start)
        day_end = datetime.datetime.fromisoformat(day_end)
        entries = analysis.getAllEntriesOfDayRange(day_start, day_end)
        try:
            keyList = tryParseList(key)
            aggregateList = tryParseList(aggregate)
            if keyList:
                if aggregateList:
                    results = analysis.aggregateMultiple(entries, keyList, aggregateList)
                else:
                    results = analysis.aggregateMultipleKeys(entries, keyList, aggregate)
            else:
                results = analysis.aggregateEntries(entries, key, aggregate)
            return jsonify(results)
        except ValueError:
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

    if day_start and day_end and key and aggregate:
        day_start = datetime.datetime.fromisoformat(day_start)
        day_end = datetime.datetime.fromisoformat(day_end)
        entries = analysis.getAllEntriesOfDayRange(day_start, day_end)
        try:
            results = analysis.aggregateEntries(entries, key, aggregate)
        except ValueError:
            abort(400)

        graph = pygal.Line()
        # graph.title = '% Change Coolness of programming languages over time.'
        graph.x_labels = [ x["timestamp"] for x in results ]
        data = [ x["value"] for x in results ]
        graph.add(results[0]["key"],  data)
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