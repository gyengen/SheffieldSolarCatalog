'''----------------------------------------------------------------------------

running.py



----------------------------------------------------------------------------'''

import engine.initialisation as ini  # Observation initialization
import engine.ssc.visual.plot as plt # For full disk visualisation
import engine.download as get        # Getting data
import engine.feature as fea         # Feature algorithms
import engine.ssc.tools.util as util # Utility library for the index function
import engine.ssc.tools.fits as fits # Export the full disk fits file
from datetime import datetime        # Estimating the running time
import logging                       # Log the errors and progress


__author__ = ["Gyenge, Norbert"]
__email__ = ["n.g.gyenge@sheffield.ac.uk"]


def start(start_time, logger, lag=360, email='scc@sheffield.ac.uk'):

    # Module 1: Download and load observation data from JSOC
    date = get.real_time_service(lag=lag)

    full_disk = get.get_data(date_of_obs=date, interval='1m@1m', email=email)
    logging.info('Observations downloaded.')

    # Module 2: Downloading and processing Sharp data
    sharp = get.get_sharp(date_of_obs=date, interval='12m@12m', email=email)
    logging.info('Sharp data downloaded.')

    # Module 3: Sunspot data based on continuum and magnetogram
    if full_disk is not False and sharp is not False:

        # Data initialization.
        ini_obs = ini.standard_multitype_ini(full_disk)
        logging.info('Data initialization.')

        # Sunspot groups contours
        Active_Regions = fea.sunspot_contours(ini_obs, sharp, 1)
        logging.info('Sunspot groups contours.')

        # Append data into database
        for obs_type in ['continuum', 'magnetogram']:

            # Select the image
            img = ini_obs[util.index(ini_obs, obs_type)]

            # Loop over each sunspot groups
            for AR in Active_Regions:

                # Additional information for processing the data
                AR.input(img, obs_type)

                # Append the database with the new information
                AR.append_sql()

                # Create figures and save png and pdf files
                AR.save()

                # Save the fits files
                AR.savefits()

            # Create the full disk image
            plt.HMI_full_disk_plot(Active_Regions, img)

            # Create the full disk image in fits format
            fits.HMI_full_disk_fits(Active_Regions, img, 0.25)

            logging.info(obs_type + ' data.')

    # Missing observation(s) error
    else:
        logging.info('Observations are not available.')

    # Return the running time
    return datetime.now() - start_time


