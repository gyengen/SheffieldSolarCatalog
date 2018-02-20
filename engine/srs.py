from ssc.get_data import*

def get_srs(observations, path):
	'''Download the latest active region information by NOAA.
	There is only one region summary for each day at 00:30am.
	Parameters
	----------
		observations - Downloaded observations

	Return
	------
		AR - solar active region summary'''

	# Check the date of the observations.

	#fname = srs.latest_obs_filename(observations)
	path = path+'data/srs/'
	fname = path+'0101SRS.txt'
	# Check SRS local avability
	av = srs.srs_avability_check(fname)

	if av is False:
		# Requested SRS is N/A in the local server
		srs_ftp.ftp_srs(fname)

	# Read the wiith Astropy Table
	AR = srs_reader.read_srs(fname)

	#
	
	# Check and rename

	return AR