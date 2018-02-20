import matplotlib.pyplot as plt
from scipy.stats import norm
import matplotlib
import numpy as np
import copy as c

__author__ = "Norbert Gyenge"
__email__ = "n.g.gyenge@sheffield.ac.uk"


def sunspot_create_row(i, NOAA, o_type, date_time, area, co, data_stat):
    ''' Mergeing the results of the sunspot data into.

    Parameters
    ----------
        o_type - observation type and feature type array
        date_time - date and time array
        area - Results of Feature_Area_Calculation() function
        co - results of Sunspot_coordinates() function
        data_stat - Results of Data_statistic() function

    Returns
    -------
        result - Merged list without dimensions'''

    # Define keys and one element for each. One row dictionary.

    result = [date_time[0],
              date_time[1],
              o_type[0],
              o_type[1],
              NOAA,
              i + 1,
              co[0].value,
              co[1].value,
              co[2].value,
              co[3].value,
              co[4].value,
              co[5].value,
              co[6].value,
              area[0].value,
              area[1].value,
              area[2].value,
              data_stat[0],
              data_stat[1],
              data_stat[2],
              data_stat[3],
              data_stat[4]]

    return result


def Initial_thresholding(ic, sg, upper=True):
    ''' Active region/quiet sun threshold estimation.

    Parameters
    ----------
        ic - Sunpy map object with normalised image by scaling_ic()
        sg - sigma
        upper - The upper or lower tail of the distribution

    Returns
       Threshold'''

    # Flattened image
    obs_flat = ic.ravel()

    # Noise (quiet sun) fitting with Gaussian distribution
    mu, std = norm.fit(obs_flat[~np.isnan(obs_flat)])

    # 5 sigma is considered as sunspot
    if upper is True:
        threshold = mu + (sg * std)

    if upper is False:
        threshold = mu - (sg * std)

    return threshold


def index(obs, mea):
    ''' This method finds the index of an image.

    Parameters
    ----------
        obs - Sunpy map object list
        mea - string

    Return
    ------
        continuum_index - index'''

    for i in range(len(obs)):

        #  Using measurement information
        if str(obs[i].measurement).split()[0] == str(mea):
            index = i

    return index


def scaling_ic(ic):
    ''' Continuum image normalization.

    Parameters
    ----------
        ic - Sunpy map object continuum image

    Return
    ------
        ic - Normalized image 2d numpy array'''
    im = np.array(ic.data)

    return c.copy((1 - (im - np.nanmin(im)) / (np.nanmax(im) - np.nanmin(im))) * 100)


def shiftedColorMap(cmap, start=0, midpoint=0.5, stop=1.0, name='shiftedcmap'):
    '''Function to offset the "center" of a colormap. Useful for
    data with a negative min and positive max and you want the
    middle of the colormap's dynamic range to be at zero

    Parameters
    ----------
      cmap - The matplotlib colormap to be altered

      start - Offset from lowest point in the colormap's range. Defaults to 0.0
      		  (no lower ofset). Should be between 0.0 and `midpoint`.

      midpoint - The new center of the colormap. Defaults to  0.5 (no shift).
      			 Should be between 0.0 and 1.0. In general, this should be
      			 1 - vmax/(vmax + abs(vmin)) For example if your data range from 
      			 -15.0 to +5.0 and you want the center of the colormap at 0.0, `midpoint`
          		 should be set to  1 - 5/(5 + 15)) or 0.75

      stop - Offset from highets point in the colormap's range.
          	 Defaults to 1.0 (no upper ofset). Should be between
          	 `midpoint` and 1.0.

     Returns
     -------
     	newcmap - New colormap.'''
    
    cdict = { 'red': [], 'green': [], 'blue': [], 'alpha': []}

    # regular index to compute the colors
    reg_index = np.linspace(start, stop, 257)

    # shifted index to match the data
    shift_index = np.hstack([np.linspace(0.0, midpoint, 128, endpoint=False), 
        					 np.linspace(midpoint, 1.0, 129, endpoint=True)])

    for ri, si in zip(reg_index, shift_index):

        r, g, b, a = cmap(ri)

        cdict['red'].append((si, r, r))
        cdict['green'].append((si, g, g))
        cdict['blue'].append((si, b, b))
        cdict['alpha'].append((si, a, a))

    newcmap = matplotlib.colors.LinearSegmentedColormap(name, cdict)
    plt.register_cmap(cmap=newcmap)

    return newcmap

def fmt(x, pos):
    a, b = '{:.1e}'.format(x).split('e')
    b = int(b)
    return r'${} \times 10^{{{}}}$'.format(a, b)

