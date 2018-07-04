from datetime import date, timedelta, datetime
import drms
import drms.error
import sunpy.map

def get_data(path,date,interval,email):

	'''

	Parameters
	----------
		- Path
		- Date
		- Interval
		- Email

	Returns
	-------
		observations - Sunpy map object

	Notes
	------

	Observation downloading and loading module.
	The DRMS module requires a query string to search for the desired observation
	files. The first half of the function is used to create a varible query string
	and the second half downloads the observations using the query string. The last
	line loads the observation files. This is done as the downloading variable
	produces a table containing the location of the downloaded files and this
	can be used to load the observation files for convenience.

	Example query strings are

	EXAMPLE

	'Series' + 'Year.Month.Day' + '_' + 'Hour:Minute:Second' + '_TAI/' + interval

	Note that the hour:minute:second does not need to be specified and defaults
	to midnight.

	Currently downloading Continuum and Magnetogram observations.
	'''
	try:
		# Building Query string
		ic_series = 'hmi.ic_45s'
		m_series = 'hmi.m_45s'
		ic_query_string = ic_series + '[' + date  + '_TAI/' + interval +']'
		m_query_string = m_series + '[' + date + '_TAI/' + interval +']'

		# Logging into JSOC database and requesting files
		client = drms.Client(verbose=True)
		print (ic_query_string)
		# Downloading observation files.
		ic_client = client.export(ic_query_string, method='url', protocol='fits',email=email)
		print('\nRequest URL: %s' % ic_client.request_url)
		print('%d file(s) available for download.\n' % len(ic_client.urls))
		ic=ic_client.download(path + 'data/obs/')

		m_client = client.export(m_query_string, method='url', protocol='fits', email=email)
		print('\nRequest URL: %s' % m_client.request_url)
		print('%d file(s) available for download.\n' % len(m_client.urls))
		m=m_client.download(path + 'data/obs/')


		# Loading observations
		# This is done as the downloading variable contains a table with useful data
		file_list = list(ic['download']) + list(m['download'])
		observations = sunpy.map.Map(file_list)
	except drms.error.DrmsExportError:
		print ("JSOC Server failed to load observation files in time, breaking engine")
		observations = False
		return observations

	return observations
