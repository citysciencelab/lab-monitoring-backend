from flask import Flask, request, render_template
from database_connector import getUserId, appendData, makeUser, getFullDump

app = Flask(__name__)

@app.route('/login', methods = ['POST', 'GET'])
def login():
    if request.method == 'POST':
        username = request.form['nm']
    else:
        username = request.args.get('nm')
    try:
        userid = str(getUserId(username))
    except ValueError:
        userid = makeUser(username)
    return str(userid)

@app.route('/submit', methods = ['POST'])
def submit():
    if request.method == 'POST':
        if not "id" in request.form:
            raise ValueError("no user id supplied!")
        userid = request.form['id']
        data = dict(request.form)
        del data["id"]
        appendData(userid,data)
    return str(getFullDump())

@app.route('/')
def index():
    return render_template('./test_form.html')

if __name__ == '__main__':
    app.run(debug=True)