from astropy.coordinates import SkyCoord
from astropy import units as u
from astropy.wcs.utils import wcs_to_celestial_frame
from copy import copy
import numpy as np


def LOS2Bz(observation):
    '''Estimate the Bz magnetic field from LOS megnetogram.

    Parameters
    ----------
        observation - Sunpy map object, magnetogram

    Returns
    -------
        observation - Sunpy map object, projection effect estimated

    Reference
    ---------
        Hagyard, M. J., Changes in measured vector magnetic fields when transformed into
        heliographic coordinates, Solar Physics (ISSN 0038-0938), vol. 107, no. 2, 1987

    Example
    -------
    >>> import sunpy.map
    >>> observation = sunpy.map.Map('hmi.m_45s.2015.01.01_12_01_30_TAI.magnetogram.fits')
    >>> observation = observation.rotate()
    >>> observation = LOS2Bz(observation)
    >>> observation.plot(vmin = -3000, vmax = 3000)
    >>> observation.draw_grid()
    >>> observation.draw_limb()'''

    # Keep the original Sunpy map
    observation = copy(observation)

    # Read the basic physical properties
    l0 = 0
    b0 = np.radians(observation.carrington_longitude).value
    nx, ny = observation.dimensions

    # Range of the ROI; full disk
    obs_corner =  observation.pixel_to_world([0 * u.pix, nx] * u.pix, [0 * u.pix, ny] * u.pix)

    r_x, r_y = obs_corner.Tx ,obs_corner.Ty

    # Convert from float to int
    r_x = r_x.astype('int')
    r_y = r_y.astype('int')

    # Create an arcsec grid.
    xv, yv = np.meshgrid(np.linspace(r_x[0].value, r_x[1].value, nx.value.astype('int')),
                         np.linspace(r_y[0].value, r_y[1].value, ny.value.astype('int')), indexing='xy')

    # add units
    xv = xv * u.arcsec
    yv = yv * u.arcsec

    # Calculate each pixel's heliographics coordinate.
    co = SkyCoord(xv, yv, frame=wcs_to_celestial_frame(observation.wcs)).heliographic_stonyhurst

    # Create latitude and longitude mask and convert them to radians
    b_mask = np.radians(co.lat).value
    l_mask = np.radians(co.lon).value

    # Bz estimation for each pixel
    f0 = np.cos(b0) * np.cos(b_mask) * np.cos(l_mask - l0)
    f1 = np.sin(b0) * np.sin(b_mask)

    observation._data = observation.data / (f0 + f1)

    return observation
