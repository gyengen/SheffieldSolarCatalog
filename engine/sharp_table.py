from astropy.io import fits
from astropy.coordinates import SkyCoord, CartesianRepresentation
from astropy import units as u
from astropy.table import Table, Column
from sunpy.coordinates import frames
from ssc.feature.harpnum_to_noaa import harp_noaa
import datetime
import os
import numpy as np
import sunpy.map

''' Create sharp number table for AR

Parameters
----------
    Location - Location and filenames of SHARP data


Return
------
	t - AR table for SHARP data
'''

def sharp_table(location):

    print (len(location), "active regions detected by Sharp")
    # Creating empty table
    t = Table(names=('NOAA_Nmbr','HARPNUM','box_y2','box_y1','box_x2','box_x1'),
              dtype=('S6','S6','f8','f8','f8','f8'))

    # Unsure what dtype box_xx should be
    for file in location:

        sunpymap=sunpy.map.Map(file)  # Is this useful?
        hdul = fits.open(file)


        # Unsure what dtype box_xx should be

        # Finding Coordinate Headers - In Lambert Cylindrical Equal-Area
        Sharp_time = hdul[0].header[11]
        LAT_MIN = hdul[0].header[112]
        LAT_MAX = hdul[0].header[114]
        LON_MIN = hdul[0].header[113]
        LON_MAX = hdul[0].header[115]
        HARPNUM = hdul[0].header[84]
        # Processing data

        # Function that converts HARPNUM into NOAA number if NOAA number exists

        box_min = SkyCoord(LAT_MIN * u.deg,LON_MIN * u.deg, frame =
                           frames.HeliographicStonyhurst, obstime = Sharp_time)
        box_max = SkyCoord(LAT_MAX * u.deg,LON_MAX * u.deg, frame =
                           frames.HeliographicStonyhurst, obstime = Sharp_time)

        box_min_pix = sunpymap.world_to_pixel(box_min)
        box_max_pix = sunpymap.world_to_pixel(box_max)

        # Round to forth decimal place
        box_x1 = np.round(box_min_pix[0],4)
        box_x2 = np.round(box_max_pix[0],4)
        box_y1 = np.round(box_min_pix[1],4)
        box_y2 = np.round(box_max_pix[1],4)

        NOAA_num = harp_noaa(HARPNUM)

        t.add_row([NOAA_num, HARPNUM, box_y2,box_y1,box_x2,box_x1])

    return t
