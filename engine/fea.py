from astropy.coordinates import SkyCoord
from sunpy.coordinates import frames
from astropy import units as u
from ssc.feature import*
from ssc.visual import*
from ssc.tools import*


__author__ = "Norbert Gyenge"
__email__ = "n.g.gyenge@sheffield.ac.uk"


def sunspot_contours(initialized_observations, AR_summary, mpix=5):
    ''' Define the Sunspot group contours

    Parameters
    ----------
        initialized_observations - Sunpy map object

    Returns
    -------
    '''

    # Save the contours
    contours = []

    # Find the continuum image
    continuum_index = util.index(initialized_observations, 'continuum')

    # Find the magnetogram image
    continuum_img = initialized_observations[continuum_index]

    # Loop over the active regions
    for active_region in AR_summary:

        # Cut the ROI
        dx = [active_region['box_x1'], active_region['box_x2']] * u.arcsec
        dy = [active_region['box_y1'], active_region['box_y2']] * u.arcsec

        bl = SkyCoord(dx[0], dy[0], frame=frames.Helioprojective)
        tr = SkyCoord(dx[1], dy[1], frame=frames.Helioprojective)

        c_sub = continuum_img.submap(bl, tr)

        # Scaleing and normalization
        c_sub = util.scaling_ic(c_sub)

        # Simple method to estimate the active region/quiet sun ithreshold
        TH = util.Initial_thresholding(c_sub, sg=5, upper=True)

        # Initial binary mask (1 if pixel > TH and 0 else)
        ini = msnakes.Morphological_Snakes_mask(c_sub, TH)

        # Morphological_Snakes for finding the boundary of the sunspots
        AR_mask = msnakes.Morphological_Snakes(c_sub, ini)

        # Create contours from binary masks
        AR_contours = contour.Morphological_Snakes_contours(AR_mask, mpix)

        # Filter the contours, no negative contour; no negative peak contour
        AR_contours = contour.Contours_size_filter(AR_contours, mpix)

        # Append with new data
        contours.append(AR_contours)

    return contours


def sunspot_data(initialized_observations, AR_summary, s_contours, o_type):
    '''s_contours

    Parameters
    ----------

    Returns
    -------

    Notes
    -----
    Please note that s_contours is a nested list:
    s_contours[i][j][k][l], where
    i = number of active region
    j = umbra or penumbra conturs (0 or 1)
    k = number of the individual spot whitin the active region
    l = x or y coordinates of the contour (0 or 1).'''

    # Find the image index
    index = util.index(initialized_observations, o_type)

    # Define the images
    img = initialized_observations[index]

    # Loop over each sunspot groups
    for i in range(len(s_contours)):

        # Select the umbrae and penumbrae whitin an active region
        p_con = s_contours[i][0]
        u_con = s_contours[i][1]

        # Cut the ROI
        dx = [AR_summary[i]['box_x1'], AR_summary[i]['box_x2']] * u.arcsec
        dy = [AR_summary[i]['box_y1'], AR_summary[i]['box_y2']] * u.arcsec

        bl = SkyCoord(dx[0], dy[0], frame=frames.Helioprojective)
        tr = SkyCoord(dx[1], dy[1], frame=frames.Helioprojective)

        # Define the submap
        sub = img.submap(bl, tr)

        # NOAA number of the group
        NOAA = int(AR_summary[i]['Nmbr']) + 10000

        # Sunspot group visualize (submap + counturs)
        plot.AR_plot(sub, s_contours[i], AR_summary[i], o_type)

        # Penumbra data
        obs_type = [o_type, 'penumbra']
        raw_data.sunspot_sql_append(p_con, img, sub, NOAA, dx, dy, obs_type)

        # Umbra data
        obs_type = [o_type, 'umbra']
        raw_data.sunspot_sql_append(u_con, img, sub, NOAA, dx, dy, obs_type)

    return 0
