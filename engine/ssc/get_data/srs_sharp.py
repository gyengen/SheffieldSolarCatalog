from __future__ import absolute_import, division, print_function
import os
import drms
import datetime


'''
Parameters
----------
observations - Downloaded observations

Return
------
AR - solar active region summary

Downloads latest active region SHARP data from JSOC
Two different series are available, the definitive and the real
time data. The definitive data lags behind the real data by some days (CHECK!)
whereas the real time data provides data in real time but the results may not
be accurate (why?).

These two data series are called
Definitive -
hmi.sharp_720s
hmi.sharp_720s_nrt

'''
def Sharp_definitive(date,Start_time,interval):
    ### Preconfiguration ###

    ## Creating download folder with variable name
    # Desired start date and time
    date = '2018.03.31' #YY.MM.DD
    Start_time = '01:20:00'

    # Download interval - can be in years, months, days or hours - y, m, d, h
    # Download all files in time period of x, at intervals of y xh @ yh
    interval = '1h@10m'

    # Creating Download directory if it does not exist
    out_dir = os.path.join('data/SRS_Sharp/', 'sharp_%s' % date)
    if not os.path.exists(out_dir):
    	os.makedirs(out_dir)

    ## Creating search and downloaded string. Search string used to see how many Active
    # regions are detected, and download string is used to download files

    # Series - Can use either hmi.sharp_cea_720s or hmi.sharp_720s_cea_nrt
    series = 'hmi.sharp_cea_720s'

    # DL_string used to search for file
    Search_string = series + '[]' + '[' + date + '_' + Start_time + '_TAI/' + interval +']'
    #DL_string =  Search_string + '{continuum, magnetogram, bitmap}'
    DL_string =  Search_string + '{bitmap}'


    # Use 'as-is' instead of 'fits' if record keywords are not needed in the
    # FITS header. Reduces the server load!
    export_protocol = 'fits'
    #export_protocol = 'as-is'

    # Email is needed to log in to system
    email = 'vinhvu1995@gmail.com'

    ### Preconfiguration finished ###

    # Log in to DRMS client
    c = drms.Client(verbose=True)

    # Printing out how many HARPNUM are found

    s = c.query(Search_string, key='HARPNUM')
    cs = s['HARPNUM']
    print (len(set(cs)),"Real-time Active Regions detected by SHARP")

    # Downloading files
    r = c.export(DL_string, method='url', protocol='fits', email=email)
    print('\nRequest URL: %s' % r.request_url)
    print('%d file(s) available for download.\n' % len(r.urls))
    r.download(out_dir)

    # function that analyses downloaded FITS file data
    # sharp_table.py

def Sharp_nrt(interval):

	### Preconfiguration ###

	## Creating download folder with variable name
	now =  datetime.datetime.now()
	datefile = str(now.year) + '-'+str(now.month) +'-'+ str(now.day)

	# Creating Download directory if it does not exist
	out_dir = os.path.join('data/SRS_Sharp_nrt/', 'sharp_%s' % datefile)
	if not os.path.exists(out_dir):
		os.makedirs(out_dir)

	## Creating todays search query

	# Series - Can use either hmi.sharp_cea_720s or hmi.sharp_720s_cea_nrt
	series = 'hmi.sharp_720s_cea_nrt'

	# Todays date
	now =  datetime.datetime.now()
	month = '%02d' % now.month
	day = '%02d' % now.day
	date = str(now.year) + "." + str(month) + '.' + str(day)
	time = str(now.hour-1) + ':' + str(now.minute) + ':' + str(now.second) # Interval is 1 hour


	# Query_string used to search for file
	# Want Query_string to look like 'hmi.sharp_720s_cea_nrt[]2018.05.06_TAI/1d@10m'
	Search_string = series + '[]' + '[' + date + '_'  + '_TAI/' + interval +']'
	Query_string =  Search_string + '{continuum, magnetogram}'

	# Use 'as-is' instead of 'fits' if record keywords are not needed in the
	# FITS header. Reduces the server load!
	export_protocol = 'fits'
	#export_protocol = 'as-is'

	# Email is needed to log in to system
	email = 'vinhvu1995@gmail.com'

	### Preconfiguration finished ###

	# Log in to DRMS client
	c = drms.Client(verbose=True)
	#print(c.pkeys(r'hmi.sharp_720s'))
	#r = c.export(qstr, method='url', protocol=export_protocol, email=email)
	r = c.export(Query_string, method='url', protocol='fits', email=email)

	s = c.query(Search_string, key='HARPNUM')
	cs = s['HARPNUM']
	print (len(set(cs)),"Real-time Active Regions detected by SHARP")


	# Download selected files.
	print('\nRequest URL: %s' % r.request_url)
	print('%d file(s) available for download.\n' % len(r.urls))

	r.download(out_dir)
