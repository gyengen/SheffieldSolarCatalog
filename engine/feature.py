from astropy import units as u
import engine.ssc.sunspot.contour as con
import engine.ssc.sunspot.pixel as pix
import engine.ssc.sunspot.area as area
import engine.ssc.tools.util as util
import numpy as np
import engine.ssc.AR as AR

__author__ = "Norbert Gyenge"
__email__ = "n.g.gyenge@sheffield.ac.uk"


def sunspot_contours(initialized_obs, sharp, mpix):
    ''' Define the Sunspot group contours

    Parameters
    ----------
        initialized_observations - Sunpy map object

    Returns
    -------
    '''

    # Find the continuum image
    continuum_index = util.index(initialized_obs, 'continuum')

    # Find the magnetogram image
    continuum = initialized_obs[continuum_index]

    # Initalisation of arrays
    Active_Regions = []

    # Loop over the active regions
    for ar in sharp:

        # Only NOAA ARs
        if ar[0].header['NOAA_AR'] != 0:

            # Define the coordinates of the ROI
            bottom_left = np.array([ar[0].header['CRPIX1'],
                                    ar[0].header['CRPIX2']], dtype=int)

            top_right = np.array([(ar[0].header['CRPIX1'] +
                                   ar[0].header['CRSIZE1']),
                                  (ar[0].header['CRPIX2'] +
                                   ar[0].header['CRSIZE2'])], dtype=int)

            NOAA_num = str(ar[0].header['NOAA_AR'])

            # Mask the boundaries AR
            boundary_mask = np.array(ar[0].data)
            boundary_mask[boundary_mask == 1] = False
            boundary_mask[boundary_mask > 1] = True

            # Check rotation
            if abs(ar[0].header['CROTA2'] - 180) < 1:

                # Rotate the coordinates of ROI, bottom_left swaps top_right
                top_right, bottom_left = pix.HARProt(bottom_left, top_right, continuum)

                # Rotate the mask as well
                boundary_mask = np.rot90(boundary_mask, 2)

            # Save some info for later
            corner = [bottom_left, top_right]

            # Cut the original observations
            c_sub = continuum.submap(bottom_left * u.pixel,
                                     top_right * u.pixel)

            # Scaleing and normalization, c_sub sub is numpy array from here
            c_sub = pix.scaling_ic(c_sub.data)

            # Simple method to estimate the active region/quiet sun threshold
            full_disk = pix.scaling_ic(continuum.data)
            TH = pix.Initial_threshold(full_disk, sg=3)

            # Initial binary mask (1 if pixel > TH and 0 else)
            fea_ini = con.Morphological_Snakes_mask(c_sub, TH)

            # Morphological_Snakes for finding the boundary of the sunspots
            AR_mask = con.Morphological_Snakes(c_sub, fea_ini)

            # Apply the boundary mask
            AR_mask = [AR_mask[0] * boundary_mask, AR_mask[1] * boundary_mask]

            # Create contours from binary masks
            AR_contours = con.MS_contours(AR_mask, mpix)

            # Filter the contours, no negative contour; no negative peak
            AR_contours = con.size_filter(AR_contours, mpix)

            # Create the Active Region Object
            ARO = AR.Sunspot_groups(NOAA_num, AR_mask, AR_contours, corner)

            # Define a new array for th AROs
            Active_Regions.append(ARO)

    return Active_Regions
