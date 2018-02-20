from ssc.get_data import*


def get_data(path):
	''' This function is not ready. To do list:
	
		We need a script and downloading procedure, which;
		- Checks the observation in every X mins.
		- if there is now observation on the server, it starts to download them
		- It creates a new folder for the new observation

	Parameters
	----------
		None

	Returns
	-------
		observations - Sunpy map object

	Notes
	-----
		A new folder will be created for the dowloaded observations.'''

	# Download the new observations
	#filenames = down.download_observation(query)

	# Here we use 2 example observations. Remove these lines later
	path = path + '/data/obs/'
	filenames = ['hmi.ic_45s.2015.01.01_12_01_30_TAI.continuum.fits',
				 'hmi.m_45s.2015.01.01_12_01_30_TAI.magnetogram.fits']

	#Read the observatinon into observations object. It can contain multiple observations.
	observations = load.load_observation(path, filenames)

	print '\n'.join(filenames)

	return observations