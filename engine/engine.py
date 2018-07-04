from datetime import date, timedelta, datetime
import time
import get # Getting data; observations and solar region summary data (SRS)
import srs # SRS handling module
import ini # Observation initialization
import arr # Active region recognition
import fea # Feature algorithms
import logging
import drms
from ssc.get_data.sharp import get_sharp
from sharp_table import sharp_table

email = 'vqvu1@sheffield.ac.uk'
path = '/home/vinh/SSC_Vinh_reconstruction/'
show_graph = True # Doesn't show cluster graph

# Choosing date to download and analyse date.

start_date = datetime.today() - timedelta(14) # Last week
YMD = start_date.strftime("%Y") + '.' + start_date.strftime("%m") + '.' + start_date.strftime("%d")
filetime = start_date.strftime("%H") + ':' + start_date.strftime("%M")
date = YMD + '_' + filetime

obs_interval = '1m@1m' #  Can't be lower than 1 minute - available every 45 seconds
harp_interval = '10m@10m' # Can't be lower than 10 minutes - available every 12 minutes



def engine(start_time, path, logger):

    # Module 1: Download and load observation data from JSOC
    raw_observations = get.get_data(path,date,obs_interval,email)
    logging.info('Observations downloading.')
    print ("Observations downloaded")

    # Module 2: Downloading and processing SRS data. Sharp has top priority, then NOAA
    get_location = get_sharp(date)
    get_location = False
    # If sharp fails, use NOAA SRS data instead
    if get_location is False:
        logging.info('SHARP Failed. Initialising NOAA')
        AR_summary = srs.get_srs(raw_observations, path)
        logging.info('SRS information.')
    else:
        AR_summary = sharp_table(get_location)
        logging.info('SHARP data downloaded.')


    # Module 3: Data initialization.
    initialized_observations = ini.standard_multitype_ini(raw_observations)
    logging.info('Data initialization.')

    if get_location is False:
        AR_summary = arr.active_region_recognition(initialized_observations,
                                                    AR_summary,show_graph)
        logging.info('Active region recognition.')


    # Module 4: Sunspot groups contours
    s_contours = fea.sunspot_contours(initialized_observations, AR_summary)
    logging.info('Sunspot groups contours.')

    # Module 5: Append data into database
    fea.sunspot_data(initialized_observations, AR_summary, s_contours,
                    'continuum',path)
    logging.info('Continuum sunspot data.')

    fea.sunspot_data(initialized_observations, AR_summary, s_contours,
                    'magnetogram',path)
    logging.info('Magnetogram sunspot data.')
    print ("Process Complete")
    # Return the running time
    return int(time.time() - start_time)



#logger = logging.getLogger(__name__)
# FOR TESTING ONLY
logger = 0
start_time = time.time()
rt = engine(start_time, path, logger)
logging.info('Running time', rt)
print (rt)
