s2-appcert
==========

DS2OS AppCert from [HeerenSharma](https://github.com/heerensharma) 

Clone the repository

```bash
git clone https://github.com/bibstha/s2-appcert.git
cd s2-appcert
pip install -r requirements.txt
```
    
## Creating an application package.

```bash
python auth.py Appnew.jar manifest.xml model.xml dev_priv_key.pem
```

## Validating a package.zip over REST API (currently synchronous version)


###Setting up environment to run REST API
Though there is already a virtualenv setted up in the flask_api folder,
just to run things without any hassel, dependencies can be install using the provided "requirements.txt file"

```command
cd flask_api/
venv/bin/pip install -r requirements.txt
. ./venv/bin/activate
./run.py

```

###Usage of API

Curl script showing a post request which includes two files zip archive and public key of developer which 
are required to pass

```bash
curl -i -F zipdata=@packages.zip -F pubkey=@dev_pub_key.pem  http://127.0.0.1:5000/check
```

Responce in form of JSON object which has following fields:

```code
{
    "Status": "OK/Error", 
    "Message: ["Zip Archive contains all necessary files", "Public Keys match - success", "Integrity of Manifest file - success", "Integrity of Application JAR file - success"]
}
```


