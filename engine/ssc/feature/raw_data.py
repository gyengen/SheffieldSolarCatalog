from skimage import measure
from ssc.database import*
from ssc.tools import*
from pix_stat import*
import numpy as np
from coord import*
from area import*


__author__ = "Norbert Gyenge"
__email__ = "n.g.gyenge@sheffield.ac.uk"


def spot_grid(im, contour_x, contour_y):
    '''
    '''

    # Stack the x and y list of contour coordinates for skimage measure
    stack = np.stack((contour_y, contour_x), axis=-1)

    # Define the dimension of the submap
    dimension = (np.shape(im.data)[0], np.shape(im.data)[1])

    # Mask the original observation
    spot = im.data * measure.grid_points_in_poly(dimension, stack)

    return spot


def photoshpere_data_factory(img, sub, k, NOAA, c_x, c_y, dx, dy, o_type):
    '''Build the basic sunpot data for the DataFrame row by row.

    Parameters
    ----------
        photosphere_full - Sunpy map
        photosphere_sub- Sunpy submap
        i - serial number of the spot
        contour_x - x coordinates of the i-th spot
        contour_y - y coordinates of the i-th spot
        dx
        dy
        o_type

    Returns
    -------

    '''

    # Convert the spot poligon to bool mask
    spot = spot_grid(sub, c_x, c_y)
    spot_mask = np.where(spot != 0, 1, 0)

    # Calculate the spot's coordinate
    co = Sunspot_coordinates(img, dx, dy, spot)

    # Estimate the area
    area = Feature_Area_Calculation(img, dx, dy, spot_mask)

    # Calculate the photon flux
    data = Data_statistic(spot)

    # Se the date and time
    date = [str(img.date).split()[0], str(img.date).split()[1].split('.')[0]]

    # Concatenation the data and return
    row = util.sunspot_create_row(k, NOAA, o_type, date, area, co, data)

    return row


def sunspot_sql_append(contour, img, sub, NOAA, dx, dy, t):

    # Loop over the individual sunspot penumbrae
    for i in range(len(contour)):

        # Extract the x and y coordinates of the sunspot
        c_y = np.array(contour[i][0])
        c_x = np.array(contour[i][1])

        # Create a dictionary from the data
        r = photoshpere_data_factory(img, sub, i, NOAA, c_x, c_y, dx, dy, t)

        # Append the sql database with the new row of data
        sql.sunspot_continuum_table(r)

    return 0
