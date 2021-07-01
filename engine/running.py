'''----------------------------------------------------------------------------

running.py



----------------------------------------------------------------------------'''
#import gc
import engine.initialisation as ini  # Observation initialization
import engine.ssc.visual.plot as plt # For full disk visualisation
import engine.download as get        # Getting data
import engine.feature as fea         # Feature algorithms
import engine.ssc.tools.util as util # Utility library for the index function
import engine.ssc.tools.fits as fits # Export the full disk fits file


def start(full_disk, sharp, lag=False):

    # Data initialization.
    ini_obs = ini.standard_multitype_ini(full_disk)

    # Sunspot groups contours
    Active_Regions = fea.sunspot_contours(ini_obs, sharp, 10)

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


