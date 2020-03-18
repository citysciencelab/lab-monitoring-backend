from flask import Flask, request, render_template
from database_connector import getUserId, appendData

app = Flask(__name__)

@app.route('/login', methods = ['POST', 'GET'])
def login():
    if request.method == 'POST':
        user = request.form['nm']
    else:
        user = request.args.get('nm')
    print(user)
    # appendData(user,["testa","testb"])
    return "hello " + user + " your id is " + str(getUserId(user))

@app.route('/')
def index():
    return render_template('test_form.html')

if __name__ == '__main__':
    app.run(debug=True)