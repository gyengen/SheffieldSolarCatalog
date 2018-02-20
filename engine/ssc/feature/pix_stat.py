import numpy as np

__author__ = "Norbert Gyenge"
__email__ = "n.g.gyenge@sheffield.ac.uk"


def Data_statistic(spot):
    '''Calculate the basic statistic of the spot pixels.

    Parameters
    ----------
        im - Active region, IC or M.
        spot_mask - Binary map of the spot.

    Returns
    -------
        array[0] - Total photon number/photon flux/magnetic flux.
        array[1] - Mean photon number/photon flux/magnetic flux.
        array[2] - Minimum photon number/photon flux/magnetic flux.
        array[3] - Maximum photon number/photon flux/magnetic flux.
        array[4] - Standard dev of photon number/photon flux/magnetic flux.'''

    # Ignore the outside region of the spot.
    spot = np.where(spot is not False, spot, np.nan)

    # Calculate the basic stat of the mask
    stat = [np.nansum(spot), np.nanmean(spot),
            np.nanmin(spot), np.nanmax(spot), np.nanstd(spot)]

    return stat
