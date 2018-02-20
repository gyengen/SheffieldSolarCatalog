import time
import get # Getting data; observations and solar region summary data (SRS)
import srs # SRS handling module
import ini # Observation initialization
import fea # Feature algorithms
import arr # Active region recognition
import logging

#logger = logging.getLogger(__name__)

__author__ = ["Gyenge, Norbert"]
__email__  = ["n.g.gyenge@sheffield.ac.uk"]


def engine(start_time, path, logger):

	# Module 1: Get the data.
	raw_observations = get.get_data(path)
	logging.info('Observations downloading.')

	# Module 2: Download SRS data
	AR_summary = srs.get_srs(raw_observations, path)
	logging.info('SRS information.')

	# Module 3: Data initialization.
	initialized_observations = ini.standard_multitype_ini(raw_observations)
	logging.info('Data initialization.')

	# Module 4: active region recognition, using sunspot groups
	AR_summary = arr.active_region_recognition(initialized_observations, AR_summary)
	logging.info('Active region recognition.')

	# Module 5: Sunspot groups contours
	s_contours = fea.sunspot_contours(initialized_observations, AR_summary)
	logging.info('Sunspot groups contours.')

	fea.sunspot_data(initialized_observations, AR_summary, s_contours, 'continuum')
	logging.info('Continuum sunspot data.')

	fea.sunspot_data(initialized_observations, AR_summary, s_contours, 'magnetogram')
	logging.info('Magnetogram sunspot data.')

	# Return the running time
	return int(time.time() - start_time)


# FOR TESTING ONLY
start_time = time.time()
path = '/Users/norbertgyenge/Research/SSC_py/Sheffield_Solar_Catalogues/'
rt = engine(start_time, path, 0)
logging.info('Running time', rt)
print rt
# *****************