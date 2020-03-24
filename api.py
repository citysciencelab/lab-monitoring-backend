import datetime
from flask import Flask, request, render_template, jsonify, abort
from flask_cors import CORS, cross_origin
from database_connector import getUserId, getUserData, appendData, makeUser, getFullDumpJSON, checkUser
import analysis

app = Flask(__name__)
CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

@cross_origin()
@app.route('/login', methods = ['POST'])
def login():
    if request.method == 'POST':
        username = request.json['username']
    if username == "":
        abort(400)
    try:
        userid = str(getUserId(username))
    except ValueError:
        userdata = dict(request.json)
        del userdata["username"]
        userid = str(makeUser(username, userdata))
    response = {
            "id":userid,
            "userdata": getUserData(username)
        }
    return jsonify(response)

@cross_origin()
@app.route('/submit', methods = ['POST'])
def submit():
    if request.method == 'POST':
        if not "id" in request.json:
            abort(401)
        userid = request.json['id']
        if not checkUser(userid):
            abort(401)
        data = dict(request.json)
        del data["id"]
        del data["username"]
        appendData(userid,data)
    return jsonify(getFullDumpJSON())

@app.route('/')
def index():
    return render_template('./test_form.html')

@app.route('/rawdata', methods = ['POST','GET'])
def rawdata():
    if request.method == 'POST':
        day = request.json['day']
        day_start = request.json['day_start']
        day_end = request.json['day_end']
    if request.method == "GET":
        day = request.args.get("day")
        day_start = request.args.get('day_start')
        day_end = request.args.get('day_end')

    if day:
        day = datetime.datetime.fromisoformat(day)
        return jsonify(analysis.getAllEntriesOfDay(day))

    elif day_start and day_end:
        day_start = datetime.datetime.fromisoformat(day_start)
        day_end = datetime.datetime.fromisoformat(day_end)
        return jsonify(analysis.getAllEntriesOfDayRange(day_start, day_end))

@app.route('/chart_test')
def chartTest():
    import pygal
    graph = pygal.Line()
    graph.title = '% Change Coolness of programming languages over time.'
    graph.x_labels = ['2011','2012','2013','2014','2015','2016']
    graph.add('Python',  [15, 31, 89, 200, 356, 900])
    graph.add('JavaScript',    [15, 45, 76, 80,  60,  35])
    graph.add('C++',     [5,  51, 54, 102, 150, 201])
    graph.add('All others combined!',  [5, 15, 21, 55, 92, 105])
    graph_data = graph.render_data_uri()
    return render_template("test_chart.html", graph_data =  graph_data)

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0")