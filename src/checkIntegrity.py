#    This script perform various integrity checks over zip archived packaged submitted by developer
#    Usage of this script is as follows:
#     
#        python checkIntegrity.py app_zip.zip dev_pub_key.pem  
# 
#    It performs following checks:
#        1. Public key check
#        2. manifest.xml file check.
#        3. .jar file checksum taken from manifest.xml file.




from M2Crypto import RSA, X509
import filecmp 
import os,sys,re

from checksum import Check
import xml.etree.ElementTree as ET
from zipfile import ZipFile

#extracting zip in the same folder and putting the various files in place to use 

with ZipFile(sys.argv[1],'w') as zippack:
    zippack.extractall("./zippack/")
    for name in zippack.namelist():
        if re.search(".jar",name):
            JAR_FILE="./zippack/"+name    
        elif re.search(".crt",name):
            CERT_FILE="./zippack/"+name
        elif re.search("manifest.",name):
            MANIFEST_FILE="./zippack/"+name
        elif re.search("model",name):
            MODEL_FILE="./zippack/"+name
         
DEV_KEY=sys.argv[2]

#Checks at S2Store side are 3 ways:
#1. Checking the public key in certificate file
cert=X509.load_cert(CERT_FILE)
temp2=cert.get_pubkey().get_rsa()
temp2.save_pub_key("file.pem")
temp=RSA.load_pub_key(DEV_KEY)
temp.save_pub_key("file2.pem")
if filecmp.cmp("file.pem", "file2.pem", shallow=0):
    print "both public keys are matched"
else:
    print "public key integrity is abolished"
os.remove("file.pem")
os.remove('file2.pem')

#2. Checking the hash integrity of manifest.xml and model.xml file in certificate
def checkManifestIntegrity(filename,modelfile):
    temp_ext=cert.get_ext("nsManifest")
    if temp_ext.get_value()==Check.get_file_checksum(filename):
        print "Manifest integrity is checked"
    else:
        print "Manifest integrity is abolished"

    temp_ext1=cert.get_ext("nsModel")
    if temp_ext1.get_value()==Check.get_file_checksum(modelfile):
        print "Model integrity is checked"
    else:
        print "Model integrity is abolished"



    
    
    
#3. Checking the hash integrity of .jar file in manifest.xml file
def checkJarIntegrity(filename,appname):
    manifestroot=ET.parse(filename).getroot()
    hashJar=manifestroot.find('ExecutableJarHash')
    if Check.get_file_checksum(appname) == hashJar.find("Hash").text:
        print "Jar integrity is checked"
    else:
        print "Jar integrity is abolished"
    