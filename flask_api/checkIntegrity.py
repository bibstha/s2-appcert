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


class CheckIntegrity(object):
    

    def __init__(self,zipfile,pubkey,prefix_ts):
        self.zipfile = zipfile
        self.DEV_KEY = pubkey
        self.prefix_ts = prefix_ts

        
    #extracting zip in the same folder and putting the various files in place to use 
    def extractnCheckZip(self):
        with ZipFile(self.zipfile,'r') as zippack:
            zippack.extractall("./zippack/"+self.prefix_ts+"/")
            
            count=0
            for name in zippack.namelist():
                if re.search(".jar",name):
                    self.JAR_FILE="./zippack/"+self.prefix_ts+"/"+name    
                    count = count+1
                elif re.search(".crt",name):
                    self.CERT_FILE="./zippack/"+self.prefix_ts+"/"+name
                    count = count+1
                elif re.search("manifest.",name):
                    self.MANIFEST_FILE="./zippack/"+self.prefix_ts+"/"+name
                    count = count+1
                elif re.search("model",name):
                    self.MODEL_FILE="./zippack/"+self.prefix_ts+"/"+name
                    count = count+1
            if count != 4:
                return "One or more files missing in Zip archive"     
            else:
                return "OK"
    
    #Checks at S2Store side are 3 ways:
    #1. Checking the public key in certificate file
    def checkPublicKeys(self):
        self.cert=X509.load_cert(self.CERT_FILE)
        temp2=self.cert.get_pubkey().get_rsa()
        temp2.save_pub_key("file.pem")
        temp=RSA.load_pub_key(self.DEV_KEY)
        temp.save_pub_key("file2.pem")
        if filecmp.cmp("file.pem", "file2.pem", shallow=0):
            os.remove("file.pem")
            os.remove('file2.pem')
            return "OK"
        else:
            os.remove("file.pem")
            os.remove('file2.pem')
            return "public key integrity is abolished"

    #2. Checking the hash integrity of manifest.xml and model.xml file in certificate
    def checkManifestIntegrity(self):
        temp_ext=self.cert.get_ext("nsManifest")
        if temp_ext.get_value()==Check.get_file_checksum(self.MANIFEST_FILE):
            return "OK"
        else:
            return "Manifest integrity is abolished"
        '''
        #model checking code 
        temp_ext1=cert.get_ext("nsModel")
        if temp_ext1.get_value()==Check.get_file_checksum(modelfile):
            print "Model integrity is checked"
        else:
            print "Model integrity is abolished"
        '''

    #3. Checking the hash integrity of .jar file in manifest.xml file
    def checkJarIntegrity(self):
        manifestroot=ET.parse(self.MANIFEST_FILE).getroot()
        hashJar=manifestroot.find('ExecutableJarHash')
        if Check.get_file_checksum(self.JAR_FILE) == hashJar.find("Hash").text:
            return "OK"
        else:
            return "Jar integrity is abolished"
        
    

