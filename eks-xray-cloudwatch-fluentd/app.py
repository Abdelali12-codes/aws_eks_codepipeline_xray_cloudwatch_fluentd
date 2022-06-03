from aws_xray_sdk.core import xray_recorder
from aws_xray_sdk.ext.flask.middleware import XRayMiddleware
from flask import Flask,render_template, request
from flask_mysqldb import MySQL
import os 


app = Flask(__name__)

xray_daemon_address = os.environ.get('XRAY_ADDRESS') 


xray_recorder.configure(service='flask-app', daemon_address=xray_daemon_address)
XRayMiddleware(app, xray_recorder) 
plugins = ('EC2Plugin',)
xray_recorder.configure(plugins=plugins)

app.config['MYSQL_HOST'] = os.environ.get('MYSQL_HOST')
app.config['MYSQL_USER'] = os.environ.get('MYSQL_USER')
app.config['MYSQL_PASSWORD'] = os.environ.get('MYSQL_PASSWORD')
app.config['MYSQL_DB'] = os.environ.get('MYSQL_DB')

 
mysql = MySQL(app)
 

@app.route('/')  
def message():  
      return "<html><body><h1>Hi, welcome to the website</h1><h2><a href='/form'> Login</a> </h2></body></html>"  
@app.route('/form')
def form():
    return render_template('form.html')
 
@app.route('/login', methods = ['POST', 'GET'])
def login():
    if request.method == 'GET':
        return "<h1> Login via the login <a href='/form'> Form </a> </h1>"
     
    if request.method == 'POST':
        name = request.form['name']
        age = request.form['age']
        cursor = mysql.connection.cursor()
        cursor.execute(''' INSERT INTO info_table VALUES(%s,%s)''',(name,age))
        mysql.connection.commit()
        cursor.close()
        return f"Done!!"
 
if __name__ == '__main__':  
   app.run(debug = True, host='0.0.0.0', port="5000")
