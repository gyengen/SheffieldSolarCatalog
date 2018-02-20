import sunpy.map

def load_observation(path, filenames):
	'''This module loads the downloaded observations.
	Sunpy map object will be created.

	Parameters
	----------
		path - The folder of the observations, absolute or relative
		filenames - list, the downloaded observation names

	Returns
	-------
		observations - sunpy object'''

	# Slash checking 
	if (path[-1] == '/'):
		filenames = [path + fn for fn in filenames]
	else:
		filenames = [path + '/' + fn for fn in filenames]			

	# Read the observations and return them
	observation = sunpy.map.Map(filenames)
	return observation