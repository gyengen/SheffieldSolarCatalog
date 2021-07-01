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

    # Find the continuum and the magnetogram index
    continuum_index = util.index(initialized_obs, 'continuum')
    magnetogram_index = util.index(initialized_obs, 'magnetogram')

    # Find the continuum and the magnetogram image
    continuum = initialized_obs[continuum_index]
    magnetogram = initialized_obs[magnetogram_index]

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
                                   ar[0].header['CRSIZE1']) - 1,
                                  (ar[0].header['CRPIX2'] +
                                   ar[0].header['CRSIZE2'] - 1)], dtype=int)

            # Getting NOAA number from obs header
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

            # Cut the original observations
            c_sub = continuum.submap(bottom_left=bottom_left * u.pixel, top_right=top_right * u.pixel)
            m_sub = magnetogram.submap(bottom_left=bottom_left * u.pixel, top_right=top_right * u.pixel)

            # Scaleing and normalization, c_sub sub is numpy array from here, only IC
            c_sub = pix.scaling_ic(c_sub.data)
            m_sub = abs(m_sub.data)

            # Boundary max for magnetogram to find the quite sun regions
            TH_mag = np.nanstd(m_sub)
            m_sub[m_sub > 1 * TH_mag] = np.nan
            m_sub[m_sub <= 1 * TH_mag] = 1

            # Initial Threshold pixel intensity
            TH = np.nanmean(m_sub * c_sub) + 5 * np.nanstd(m_sub * c_sub)

            #import pdb; pdb.set_trace()

            #import matplotlib.pyplot as plt
            #plt.plot(test[2000, 2000:]); plt.show()
            #plt.imshow(); plt.show()

            # Find penumbra
            penumbra = con.Morphological_Snakes(c_sub, TH)

            # umbra only, cut penumbra
            c_sub = c_sub * penumbra

            # Replace zeros with np nan
            c_sub[c_sub == 0] = np.nan

            # Initial Threshold pixel intensity
            TH = np.nanmean(c_sub) + 1 * np.nanstd(c_sub)

            # Find umbra
            umbra = con.Morphological_Snakes(c_sub, TH)

            # Apply the boundary mask
            AR_mask = [penumbra * boundary_mask, umbra * boundary_mask]

            # Create contours from binary masks
            AR_contours = con.MS_contours(AR_mask, mpix)

            # Filter the contours, no negative contour; no negative peak
            AR_contours = con.size_filter(AR_contours, mpix)

            # Create the Active Region Object
            ARO = AR.Sunspot_groups(NOAA_num, AR_mask, AR_contours, [bottom_left, top_right])

            # Define a new array for th AROs
            Active_Regions.append(ARO)

    return Active_Regions
