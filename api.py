from flask import Flask, request, render_template
from flask_cors import CORS
from database_connector import getUserId, appendData, makeUser, getFullDump

app = Flask(__name__)
CORS(app)

@app.route('/login', methods = ['POST', 'GET'])
def login():
    if request.method == 'POST':
        username = request.json['id']
    else:
        username = request.args.get('id')
    try:
        userid = str(getUserId(username))
    except ValueError:
        userid = makeUser(username)
    return str(userid)

@app.route('/submit', methods = ['POST'])
def submit():
    if request.method == 'POST':
        if not "id" in request.json:
            raise ValueError("no user id supplied!")
        userid = request.json['id']
        data = dict(request.json)
        del data["id"]
        appendData(userid,data)
    return str(getFullDump())

@app.route('/')
def index():
    return render_template('./test_form.html')

if __name__ == '__main__':
    app.run(debug=True)