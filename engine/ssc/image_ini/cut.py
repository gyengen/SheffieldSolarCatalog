from astropy import units as u
import numpy as np

def solar_limb(observation):
	'''
	This procedure cut off the limb.

	Parameters
	----------
		observation - Sunpy map object

	Returns
	-------
		observation - Sunpy map object'''

	# Centre of the solar disk.
	a, b = observation.data_to_pixel(0*u.arcsec, 0*u.arcsec)
	a, b = int(a.value), int(b.value)

	# Dimensions of the observation.
	n, m = observation.dimensions.x, observation.dimensions.y
	n, m = int(n.value), int(m.value)

	# Radius of the sun in pixels.
	r = observation.rsun_obs.value / observation.scale.x.value
	r = int(r)

	# Create a grid and mask
	y_grid, x_grid = np.mgrid[0:n, 0:m]
	x_2 = (x_grid - b) ** 2
	y_2 = (y_grid - a) ** 2

	dist_grid = np.sqrt(x_2 + y_2)

	# The outside of the region of intereset will be NaN. 
	observation.data[dist_grid > r] = np.nan

	return observation
