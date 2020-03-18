from flask import Flask, request, render_template
from database_connector import getUserId, appendData, makeUser

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

@app.route('/submit', methods = ['POST', 'GET'])
def submit():
    if request.method == 'POST':
        userid = request.form['id']
        data = request.form['d1']
    else:
        userid = request.args.get['id']
        data = request.args.get('d1')
    appendData(userid,[data])
    return "successfully inserted"

@app.route('/')
def index():
    return render_template('./test_form.html')

if __name__ == '__main__':
    app.run(debug=True)