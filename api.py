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
        appendData(userid,data)
    return jsonify(getFullDumpJSON())

@app.route('/')
def index():
    return render_template('./test_form.html')

@app.route('/rawdata', methods = ['POST','GET'])
def rawdata():
    if request.method == 'POST':
        day = request.json['day']
    if request.method == "GET":
        day = request.args.get("day")
    day = datetime.datetime.fromisoformat(day)
    return jsonify(analysis.getAllEntriesOfDay(day))

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0")