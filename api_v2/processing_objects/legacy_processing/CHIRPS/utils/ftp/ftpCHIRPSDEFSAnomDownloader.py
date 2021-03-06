'''
Created on Dec 18, 2017

@author: BillyZ
'''
from ftplib import FTP
import re
import os.path as path
import gzip
import os
import sys
import CHIRPS.utils.configuration.parameters as params
import time
import json
import datetime


validFile = re.compile(r"\.tif")
gzFilePattern = re.compile(r"\.tif\.gz$")
patternWithoutgz = re.compile(r"(.*)\.gz$")
rootftpdir ='/pub/org/chg/products/EWX/data/forecasts/CHIRPS-GEFS_precip/dekad_first/'
rootoutputdir =  params.dataTypes[31]['inputDataLocation']


def gunzipFile(fileInput):
    '''
    
    :param fileInput:
    '''
    print "gunzipping the file:"+fileInput
    dirFile = path.dirname(fileInput)
    filename = path.basename(fileInput)
    m = patternWithoutgz.search(filename)
    fileWithoutgz = m.group(1)
    filetogunzip = fileInput
    fileOut = dirFile+"/"+fileWithoutgz
    f_in = gzip.open(filetogunzip, 'rb')
    f_out = open(fileOut, 'wb')
    f_out.writelines(f_in)
    f_out.close()
    f_in.close()
    
    ##Remove the gzip file
    os.remove(filetogunzip)
    print "Done gunzipping "+fileInput
    
    
    
    
def getFilesForYearAndMonth(ftp,yearToGet, monthToGet, day):
    '''
    
    :param ftp:
    :param yearToGet:
    :param monthToGet:
    '''
    ldatestring = day + " " + monthToGet + " " + yearToGet
    ldate = datetime.datetime.strptime(ldatestring, "%d %m %Y")
    print "Getting files after Year:",yearToGet," Month: ",monthToGet, " Date: ",day
    print "rootftpdir: " + rootftpdir  
    ftp.cwd(rootftpdir)
    print "Get List of files for ",yearToGet," ",monthToGet
    files = ftp.nlst()
    filteredfiles = [f for f in files if 'anom.'+str(yearToGet) in f]
    for fileToProcess in filteredfiles:
        if validFile.search(fileToProcess):
            if  re.search('anom.'+str(yearToGet), fileToProcess):
                filesplit = fileToProcess.split('.') 
                fyear = filesplit[1]
                fmonth = filesplit[2][:2]
                fday = filesplit[2][2:]
                fdatestring = fday + " " + fmonth + " " + fyear
                fdate = datetime.datetime.strptime(fdatestring, "%d %m %Y")
                if fdate > ldate:
					file_path = rootoutputdir+str(yearToGet)+"/"+fileToProcess

					print "Downloading ",fileToProcess
					fileToWriteTo = open(rootoutputdir+str(yearToGet)+"/"+fileToProcess, 'wb')
					ftp.retrbinary('RETR '+fileToProcess, fileToWriteTo.write)
					fileToWriteTo.close()
					time.sleep(1)
					if (gzFilePattern.search(fileToProcess)):
						try :
							print "Gunzipping the file: ",fileToProcess
							gunzipFile(rootoutputdir+str(yearToGet)+"/"+fileToProcess)
						except IOError:
							print "************error processing "+fileToProcess

                else:
					print "Have later data, no need to download: " +  fdatestring


def createEndDirectory(year):
    '''
    
    :param year:
    '''
    fullPath = rootoutputdir+str(year)
    if os.path.exists(fullPath) == False:
        print "Need to create "+fullPath
        os.makedirs(fullPath)
    else:
        print "Directory already exists "+fullPath

def getLastGEFSAnomDate():
	try:
		changed = False
		with open('/data/data/cserv/www/html/json/stats.json', 'r+') as f:
			data = json.load(f)
			for item in data['items']:
				if(item['name'] == 'gefsanom'):
					ldatestring = item['Latest']
					return ldatestring
	except Exception as e:
		print(e)
		pass

        
def processFilesFromLastDate(yearToGet, monthToGet, lastDate):
    '''
    
    :param yearToGet:
    :param monthToGet:
    '''
    
    print "-------------------------------Working on ",monthToGet,"/",yearToGet,"------------------------------------"
    ftp = FTP('chg-ftpout.geog.ucsb.edu')
    ftp.login()
    ftp.set_pasv(True)
    getFilesForYearAndMonth(ftp  , yearToGet, monthToGet, lastDate)
    ftp.quit()
    print "-----------------------------Done working on ",monthToGet,"/",yearToGet,"---------------------------------"


if __name__ == '__main__':
    print "Starting Downloading CHIRPS GEFS Anom Data"

    theDate = getLastGEFSAnomDate()
    day,month,year=theDate.split(' ')
    createEndDirectory(year)
    processFilesFromLastDate(year, month, day)
    #processFilesFromLastDate("2019", "01", "01")
    time.sleep(5)
    print "Done"





