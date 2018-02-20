from astropy.wcs.utils import wcs_to_celestial_frame
from astropy.coordinates import SkyCoord
from astropy.table import Table, Column
from astropy import units as u
from datetime import datetime
import numpy as np
import os


__author__ = "Norbert Gyenge"
__email__  = "n.g.gyenge@sheffield.ac.uk"


def SRS_ROI(AR):
	'''Define the cordinates of the ROI box.

	Parameters
	----------
		AR - SRS information
	Returns
	-------
		AR - Updated SRS information with ROI coordinates'''

	# Define the coordinates of ROI box
	box_x1 = AR['X2'] - AR['dx'] / 2
	box_x2 = AR['X2'] + AR['dx'] / 2
	box_y1 = AR['Y2'] - AR['dy'] / 2
	box_y2 = AR['Y2'] + AR['dy'] / 2

	# Create new Column in SRS table
	AR.add_column(Column(box_y2, name='box_y2'))	
	AR.add_column(Column(box_y1, name='box_y1'))
	AR.add_column(Column(box_x2, name='box_x2'))		
	AR.add_column(Column(box_x1, name='box_x1'))

	# Define the dimension
	AR['box_x1'].unit, AR['box_x2'].unit = u.arcsec, u.arcsec
	AR['box_y1'].unit, AR['box_y2'].unit = u.arcsec, u.arcsec

	return AR

def SRS_final(obs, AR):
	''' Update the SRS with additional coordinate transformation.
		From Helioprojective pix to helioprojective arcsec.

	Parameters
	----------
		obs - Sunpy map continuum image
		AR - SRS information

	Return
	------
		AR - Final form of the SRS data'''

	c = obs.pixel_to_data(np.array(AR['X'], dtype=int) * u.pix,
						  np.array(AR['Y'], dtype=int) * u.pix)

	# Update SRS table wirh two new columns
	AR.add_column(Column(np.round(c[1].value), name='Y2'))
	AR.add_column(Column(np.round(c[0].value), name='X2'))

	AR['B'].unit, AR['Lcm'].unit, AR['Lo'].unit  = u.deg, u.deg, u.deg
	AR['X'].unit, AR['Y'].unit = u.pix, u.pix
	AR['X2'].unit, AR['Y2'].unit = u.arcsec, u.arcsec
	AR['Location'].unit = u.deg

	# Calculate the box coordinates of the ROI
	AR = SRS_ROI(AR)

	# Remove dx and dy, no need any more
	AR.remove_column('dx')
	AR.remove_column('dy')

	return AR

def SRS_coordinate_transform(obs, AR):
	''' Convert srs position from heliographic_carrington to helioprojective system.

	Parameters
	----------
		obs - Sunpy map continuum image
		AR - SRS information

	Return
	------
		AR - SRS information with updated coordinates'''

	# Define latitude and longitude arrays
	lcm = np.array(AR['Lo'], dtype=float) - float(obs.meta['CRLN_OBS'])
	b = np.array(AR['B'], dtype=int)

	# Coordinate converting using SkyCoord
	c = SkyCoord(lcm * u.deg, b * u.deg, frame = 'heliographic_stonyhurst',
				 dateobs = obs.date, B0 = obs.meta['CRLT_OBS'] * u.deg, L0 = 0 * u.deg)

	c = c.helioprojective
	c = obs.data_to_pixel(c.Tx, c.Ty)

	# Update SRS table wirh two new columns
	AR.add_column(Column(np.round(c[1].value), name='Y'))
	AR.add_column(Column(np.round(c[0].value), name='X'))

	return AR

def srs_avability_check(fname):
	''' Checks the local avability of the requested srs information

	Parameters
	----------
		fname - SRS information to download

	Returns
	-------
		avability - bool'''

	return os.path.isfile(fname)

def latest_obs_filename(observations):
	

	'''Find the latest observation and create the filename.
	The filename format of the srs NOAA database is:
	MMDDSRS.txt, e.g. 1106SRS.txt 

	Parameters
	----------
		observations - Sunpy map object of AIA and HMI images

	Return
	------
		The date of the latest observation.'''

	suffix = 'SRS.txt'
	date_list = []
	for obs in observations:
		buff = str(obs.date).split()
		date = buff[0].split('-')
		time = buff[1].split(':')
		date_list.append(datetime(int(date[0]), int(date[1]),
						 int(date[2]), int(time[0]), int(time[1])))

	latest =  max(date_list)
	m = str(latest.month)
	d = str(latest.day)
	if len(m) == 1: m = '0' + m
	if len(d) == 1: d = '0' + d

	return m + d + suffix
