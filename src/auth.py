

# usage of this script is in creating the public keys for the developer and certificate with 
#manifest file
# Script usage is like this:
# 
#    python auth.py app_file.jar manifest_file.xml modelIO.xml private_dev_key.pem
#
#    The output of this script is a zip archive which in turn contains:
#        1. developer self signed certificate.
#        2. Application .jar file
#        3. manifest.xml file.



from socket import gethostname
from pprint import pprint
from time import gmtime, mktime
from zipfile import ZipFile

# from Crypto.PublicKey import RSA
from M2Crypto import RSA, X509, ASN1, EVP, BIO
import time
import filecmp 
import os,sys
import xml.etree.ElementTree as ET

from checksum import Check
import subprocess

#higher level prior knowledge required to fill parameters

developerId="38400000-8cf0-11bd-b23e-10b96e40000d"

JAR_FILE=sys.argv[1]
MANIFEST_FILE=sys.argv[2]
MODEL_FILE=sys.argv[3]
MAXIMIZED_MODEL_FILE="model_maximized.xml"
CERT_FILE="certificate.crt"
PRIVATE_KEY=sys.argv[4]

#create public and private key of developer
#consists of two functions: first to ge
def generate_RSAKeys(bits=2048):
    '''
    Generate an RSA keypair with an exponent of 65537 in PEM format
    param: bits The key length in bits
    Return private key and public key
    ''' 
    new_key = RSA.gen_key(bits, 65537)
    pk=EVP.PKey()
    pk.assign_rsa(new_key)
    memory = BIO.MemoryBuffer()
    new_key.save_key_bio(memory, cipher=None)
    private_key = memory.getvalue()
    with open("dev_priv_key.pem","w") as priv_key:
        priv_key.write(private_key)    
    
    new_key.save_pub_key_bio(memory)
    with open("dev_pub_key.pem","w") as pub_key:
        pub_key.write(memory.getvalue())
    return pk


# pk=generate_RSAKeys()
temp1=RSA.load_key(PRIVATE_KEY)
pk2=EVP.PKey()
pk2.assign_rsa(temp1)



#creation of certificate for the user
def createCertM2():
    #set validity period of certificate here
    cur_time = ASN1.ASN1_UTCTIME()
    cur_time.set_time(int(time.time()) - 60*60*24)

    expire_time = ASN1.ASN1_UTCTIME()
    # Expire certs in 1 hour.
    expire_time.set_time(int(time.time()) + 60 * 60 * 24)
    
    
    
    cs_cert = X509.X509()
    cs_cert.set_not_before(cur_time)
    cs_cert.set_not_after(expire_time)
    #subject name details
    cs_name=X509.X509_Name()
    cs_name.C = "DE"
    cs_name.ST = "Munich"
    cs_name.L = "Munich"
    cs_name.O = "Android developer"
    cs_name.OU = "Android developer"
    cs_name.CN = gethostname()
    
    cs_cert.set_subject(cs_name)
    cs_cert.set_issuer(cs_name)
    cs_cert.set_serial_number(1000)
    cs_cert.set_pubkey(pk2)
    cs_cert.sign(pk2, md="sha256")
    
    #put into extension details
    cs_cert.add_ext(X509.new_extension("nsManifest",Check.get_file_checksum(MANIFEST_FILE) ))
    cs_cert.add_ext(X509.new_extension("nsModel", Check.get_file_checksum(MAXIMIZED_MODEL_FILE)))
    cs_cert.save_pem(CERT_FILE)




#function call for reaching a jar file and getting maximized model.xml file in return
#Integration of Keyvan's part with it. 
#first extract the value from the Manifest.xml tag
def extract_model_id(filename):
    manifestroot=ET.parse(filename).getroot()
    modelid=manifestroot.find("RequiredContextModel").text
    model_dir=manifestroot.find("ModelDirectory").text
    return modelid, model_dir

#second function to connect with model repository
def getMaximizedModel(model_id, model_dir):
    try:
        subprocess.call(['java','-jar','modelValidator.jar','-a',model_id,'-r',model_dir,'-s',MAXIMIZED_MODEL_FILE])
    except Exception:
        print Exception.message
        
#method execution for validating model.xml file
arg1,arg2 = extract_model_id(MANIFEST_FILE)
getMaximizedModel(arg1,arg2)


#Generate public and private keys for developer
#generate_RSAKeys()



#function to create the certificate
createCertM2()




#zip archiving the jar file, manifest file and certificate file
with ZipFile('packages.zip','w') as myzip:
    myzip.write(CERT_FILE)
    myzip.write(MANIFEST_FILE)
    myzip.write(JAR_FILE)
 













