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

## Validating a package.zip file

```bash
python checkIntegrity.py packages.zip dev_pub_key.pem
```
