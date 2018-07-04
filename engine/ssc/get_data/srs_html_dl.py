import datetime
import urllib.request   # the lib that handles the url stuff
import time
import os


def srs_html_dl(fname):


    #Get todays date
    date=datetime.datetime.utcnow()
    print ("Starting NOAA SRS Download",date.date())
    #Creating unique filename
#    filename = 'SRS_%s' %date.date()
    #Creates and writes innto a new file called 'filename'
    with open(fname, "w") as f:
    #Goes to website and saves the data into The 'data' variable
        data = urllib.request.urlopen('http://services.swpc.noaa.gov/text/srs.txt')
        #Iterates lines in website and writes it into file
        for line in data:
            f.write(str(line))
            f.write(os.linesep)
        f.close()
