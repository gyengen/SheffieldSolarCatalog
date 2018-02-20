from astropy import units as u
from ssc.get_data import*
from ssc.feature import*
from ssc.tools import*

__author__ = "Norbert Gyenge"
__email__  = "n.g.gyenge@sheffield.ac.uk"


def active_region_recognition(initialized_observations, AR_summary):
	'''Sunspot recognition and identification method. This method uses 
	HMI continuum and magnetogram observations to reveal the physical
	properties of the sunspot groups, such as, position, location, magnetic
	field, etc...

	Parameters
	----------
		initialized_observations - Sunpy map object

	Returns
	-------'''

	# Find continuum image

	continuum_index  = util.index(initialized_observations, 'continuum')
	continuum_img = initialized_observations[continuum_index]

	print continuum_img.date, continuum_img.detector, continuum_img.measurement

	# SRS coordinate transformation heliographics to heliocentric
	AR_summary = srs.SRS_coordinate_transform(continuum_img, AR_summary)

	# Scaling and normalisation for the clustering method, which estimates the ARs' position
	ic = util.scaling_ic(continuum_img)

	# Simple method to estimate the active region/quiet sun ithreshold
	TH = util.Initial_thresholding(ic, 5, upper=True)

	# Clustering method, individual sunspot into sunspot groups
	cluster_centre = cluster.Sunspot_Groups_Clustering(ic, TH, 5)

	# Plot the result of the clustering method - DEVELOPING ONLY - COMMENT IT OUT
	#Plot_Sunspot_Groups_Clustering

	# Associate the NOAA number with the identified sunspot clusters, update AR information
	AR_summary = noaa.NOAA(cluster_centre, AR_summary)

	# SRS finalisation
	AR_summary = srs.SRS_final(continuum_img, AR_summary)

	return AR_summary
