#!venv/bin/python
from flask import Flask, url_for, request, Response
from checkIntegrity import CheckIntegrity
from werkzeug.utils import secure_filename
import os
import shutil
import time
import datetime
import json
import tempfile

UPLOAD_FOLDER = './Uploads/'
ALLOWED_EXTENSIONS = set(['zip','pem'])

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/')
def index():
	return "Hello world!!"


@app.route('/developer')
def api_developer():
	if 'name' in request.args:
		return "Who is the worst REST API developer? "+request.args['name']
	else:
		return "It's mistake of Heeren."

def allChecks(zipfile, pub_key, prefix_ts):
	#list to create JSON response object
	response = []

	chkI  = CheckIntegrity(zipfile,pub_key,prefix_ts)

	status = "OK"
	status_msg_array = []

	check1 = chkI.extractnCheckZip()
	if check1 == "OK" and status == "OK":
		status_msg_array.append("Zip Archive contains all necessary files")
	else:
		status = "Error"
		status_msg_array.append(check1)

	check2 = chkI.checkPublicKeys()
	if check2 == "OK" and status == "OK":
		status_msg_array.append("Public Keys match - success")
	else:
		status = "Error"
		status_msg_array.append(check2)

	check3 = chkI.extractnCheckZip()
	if check3 == "OK" and status == "OK":
		status_msg_array.append("Integrity of Manifest file - success")
	else:
		status = "Error"
		status_msg_array.append(check3)

	check4 = chkI.extractnCheckZip()
	if check4 == "OK" and status == "OK":
		status_msg_array.append("Integrity of Application JAR file - success")
	else:
		status = "Error"
		status_msg_array.append(check4)

	response.append({'Status': status, 'Message': status_msg_array})

	return json.dumps(response)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


# a simple hack to put time till microseconds precision for getting perfect unique name
# just a added value.  
def hacktimestamp():
	return str(int(time.mktime(datetime.datetime.now().timetuple())*1e6 + datetime.datetime.now().microsecond))


@app.route('/check',methods=['POST'])
def api_check():
	if request.method == 'POST':
		#some magic to get the file uploads from the user
		#two files needed: 1. zip archive 2. public key		
		zipfile = request.files['zipdata']
		pub_key = request.files['pubkey']
		#time stamp prefix for making more unique name of temporary file names
		prefix_ts=hacktimestamp()
		if zipfile and allowed_file(zipfile.filename):
			# mimetype = zipfile.content_type
			zipfilename=prefix_ts+tempfile.NamedTemporaryFile(suffix=".zip").name[5:]
        	zipfile.save(os.path.join(app.config['UPLOAD_FOLDER'], zipfilename))
        	# print tempfile.gettempdir()
        	
		if pub_key and allowed_file(pub_key.filename):
			# mimetype = zipfile.content_type
			pub_keyname=prefix_ts+tempfile.NamedTemporaryFile(suffix=".pem").name[5:]
        	pub_key.save(os.path.join(app.config['UPLOAD_FOLDER'], pub_keyname))
        	# print tempfile.gettempdir()
        #full path names of zip file and public key	
        path_zip = UPLOAD_FOLDER+zipfilename
        path_key = UPLOAD_FOLDER+pub_keyname
        print path_key
        print path_zip
        try:
        	resp=Response(allChecks(path_zip,path_key,prefix_ts), status=200, mimetype='application/json')
        finally:
        	os.remove(path_zip)
        	os.remove(path_key)
        	shutil.rmtree('./zippack/'+prefix_ts+"/")
        return resp


if __name__ == '__main__':
	app.run(debug = True)


