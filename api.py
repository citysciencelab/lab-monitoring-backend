from flask import Flask, request, render_template, jsonify, abort
from flask_cors import CORS, cross_origin
from database_connector import getUserId, appendData, makeUser, getFullDumpJSON, checkUser

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
        userid = makeUser(username)
    return jsonify(userid)

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

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0")