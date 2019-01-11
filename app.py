from flask import Flask
from flask import jsonify,request,send_from_directory
from datetime import datetime
import os,json
import numpy as np
from io import BytesIO
from PIL import Image
import base64
from hello.bw2color import BW2Color

BASE = os.path.dirname(os.path.abspath(__file__))
app = Flask(__name__,static_url_path='')
@app.after_request
def after_request(response):
  response.headers.add('Access-Control-Allow-Origin', '*')
  response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,cache-control')
  response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
  return response

@app.route('/')
def homepage():
    the_time = ""

    return """
    <h1>Hello heroku</h1>
    <p>It is currently {time}.</p>

    <img src="http://loremflickr.com/600/400">
    """.format(time=the_time)

@app.route('/img/<path:path>')
def send_file(path):
    return send_from_directory('img', path)

@app.route('/bw2color', methods=['POST','OPTIONS'])
def bw2color():
    if request.method == 'POST':
       
        r = request.get_json()
        # received_json_data=json.loads(request.body.decode("utf-8"))
        # print(json.dumps(request.json))
        # print(r['rawimg'])
        # for key in req:
        #     print "key: %s , value: %s" % (key, mydictionary[key])
        data={}
        status = False
        error = ""
        try:
            data = BW2Color(r['rawimg'])
            status = True
        except Exception as e:
            print(e)
            error = e
        return jsonify(status=status, data=data, error=str(error))
    else:
        return ""

if __name__ == '__main__':
	app.debug = True
	app.use_reloader = True
	port = int(os.environ.get('PORT', 5000))
	app.run(host='0.0.0.0', port = port)
    # app.run(debug=True, use_reloader=True)