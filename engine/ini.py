from ssc.image_ini import *
import numpy as np
import sunpy.instr.aia


def standard_multitype_ini(observations):
	'''Standard initialization for different kind of observation. The initialization
	contains ratiation, limb darkening correction, Bz estimation and limb out region
	remove.

	Parameter
	---------
		observations - Sunpy map object, it can contain multiple images and measurements.

	Return
	------
		observations - Sunpy map object with modified data'''

	# Create a new list for the initialized observations
	initialized_observations=[]

	for obs in observations: 

		print obs.date, obs.detector, obs.measurement, '\nImage De-Rotation'

		if obs.detector == 'HMI':
			# Replace np.nan-s with zero for rotating 
			obs._data = np.nan_to_num(obs.data)

			# Rotate the observations
			obs = obs.rotate()

			# Limb darkening correction, only HIM white lighe image
			if obs.measurement == 'continuum':
				print 'Limb darkening correction'
				obs = dark_limb.limb_darkening_correct(obs, limb_cut=False)

			# Longitudinal magnetic field to Bz estimation. Slow procedure, we need a faster solution (12 secs)
			if obs.measurement == 'magnetogram':
				print 'Bz estimation'
				#obs = blbz.LOS2Bz(obs)

			# Cut the limb and replace outlimb region with np.nan
			print 'Limb cut'
			obs = cut.solar_limb(obs)

		if obs.detector == 'AIA':
			# Processes a level 1 AIAMap into a level 1.5 AIAMap

			print 'AIA lev1 to lev1.5'
			obs = sunpy.instr.aia.aiaprep(obs)

		# Append the new maps
		initialized_observations.append(obs)

	# Delete raw observations
	del observations

	return initialized_observations