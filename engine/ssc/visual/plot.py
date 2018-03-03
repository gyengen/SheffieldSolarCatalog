from mpl_toolkits.axes_grid1 import make_axes_locatable
import matplotlib.ticker as ticker
import matplotlib.pyplot as plt
from astropy import units as u
import matplotlib as mpl
from ssc.tools import*
import sunpy.cm as cm
import scipy.ndimage
import numpy as np
import os


__author__ = "Norbert Gyenge"
__email__  = "n.g.gyenge@sheffield.ac.uk"


def contour_plot(contour, ax, color, font_color):
    ''' Plot the contours

    Parameters
    ----------
        contour - 

        ax - Matplotlib axes

        color - 

        fontcolor - 

    Returns
    -------
    '''

    for i, spot_position in enumerate(contour):

        # Plot the penumbra
        ax.plot(spot_position[1], spot_position[0], linewidth=1, color=color)

        # Setup font position
        font_position = (np.nanmean(spot_position[1]), np.nanmin(spot_position[0]))

        # Plot the penumbra id 
        ax.annotate(str(i+1), xy= font_position, xycoords='data', verticalalignment='top', color=font_color)

    return 0


def im_axes(ax):
    ''' Image axes properties

    Parameters
    ----------
        ax - Matplotlib axes.

    Returns
    -------
        None'''

    # Remove the upper and right ticks.
    ax.spines['right'].set_color('none')
    ax.spines['top'].set_color('none')

    # Remove the upper and right ticks.
    ax.xaxis.set_ticks_position('bottom')
    ax.yaxis.set_ticks_position('left')

    # Axes offset
    ax.spines['bottom'].set_position(('axes', -0.025))
    ax.spines['left'].set_position(('axes', -0.025))

    # Direction of the ticks out.
    ax.get_yaxis().set_tick_params(which='both', direction='out')
    ax.get_xaxis().set_tick_params(which='both', direction='out')

    # Remove the default grid
    ax.grid(b=True, linewidth=0)

    return 0

def co_axes(ax, im, sub):
    ''' Contour axes properties

    Parameters
    ----------
        ax - Matplotlib axes.
        sub - Image

    Returns
    -------
        None'''

    # Set pix-pix axes limits.
    ax.set_xlim([0, sub.dimensions[0].value])
    ax.set_ylim([0, sub.dimensions[1].value])

    # Hide all axes
    ax.axes.get_xaxis().set_visible(False)
    ax.axes.get_yaxis().set_visible(False)

    divider = make_axes_locatable(ax)
    cax = divider.append_axes("right", size="2.5%", pad=0.15)

    # Hide new axes
    #cax.axes.get_xaxis().set_visible(False)    
    #cax.axes.get_yaxis().set_visible(False)

    # Add the colour bar.
    cbx = plt.colorbar(im, format=ticker.FuncFormatter(util.fmt),
                       drawedges=False, cax=cax)

    # No xolour bar frame.
    cbx.outline.set_visible(False)

    # Setup colourbar ticks.
    cbx.ax.tick_params(axis='y', direction='out')

    return 0


def cb(ax, im, sub):
    ''' Add a colour bar at the right hand side of the image.
    create an axes on the right side of ax. The width of cax will be 5%
    of ax and the padding between cax and ax will be fixed at 0.05 inch.

    Parameters
    ----------
        ax - Matplotlib axes.

    Returns
    -------
        None'''

    # Location setup
    divider = make_axes_locatable(ax)
    cax = divider.append_axes("right", size="2.5%", pad=0.15)

    # Add the colour bar.
    cbx = plt.colorbar(im, format=ticker.FuncFormatter(util.fmt),
                       drawedges=False, cax=cax)

    # No xolour bar frame.
    cbx.outline.set_visible(False)

    # Setup colourbar ticks.
    cbx.ax.tick_params(axis='y', direction='out')

    # Colorbar name
    if sub.detector == 'AIA':
        title = 'n [1]'

    if sub.detector == 'HMI':
        if sub.measurement == 'continuum':
            title = r'$\phi$ [1/s]'

        if sub.measurement == 'magnetogram':
            title = 'M [G]'

    cbx.ax.set_title(title)

    return 0


def path_define(date, AR_summary, obs_type):
    ''' Save folder definition

    Parameters
    ----------
        date - The date of the observation

    Returns
    -------
        path - string, output folder'''

    # Split the date into date and time
    date = str(date).split()

    # Absolute path
    path = str(os.getcwd())

    # Find the parent directory
    path = os.path.abspath(os.path.join(path, os.pardir))

    print obs_type, str(int(AR_summary['Nmbr']) + 10000)
    filename = 'AR_' + str(int(AR_summary['Nmbr']) + 10000) + '_' + obs_type
    filename = filename + str(date[0]) + '_' + str(date[1]).split('.')[0]
    filename = filename + '.png'

    return path + '/database/img/' + date[0] + '/', filename


def AR_plot(sub, contour, AR_summary, obs_type):
    '''Create a fancy plot of the active regions

    TIP Bokeh, Vispy, mpld3


    Parameters
    ----------
        c_sub - 

        contour - 

    Returns 
    -------
    '''

    # Submap normalization and scaling
    #if obs_type == 'continuum':
    #    sub.data = util.scaling_ic(sub)

    # Colormap
    #colormap = util.shiftedColorMap(mpl.cm.seismic, np.nanmin(sub.data), 0, np.nanmax(sub.data))


    # Resample your data grid by a factor of 1 sigma using gaussian smoothing.
    sub._data = scipy.ndimage.gaussian_filter(sub.data, sigma=(1, 1), order=0)

    # Set up the qoutput image size, 16:9 ratio, dpi = 600: print quality
    fig = plt.figure(figsize=(12,12*0.5625), dpi=1000, facecolor="#eff0f4", edgecolor='#535353')

    # Define the default axes. This is arcsec-arcsec image.
    arc_arc = fig.add_subplot(1,1,1)

    # Plot the active region
    im = sub.plot(axes=arc_arc)

    # Create the latitude / longitude grid
    #sub.draw_grid(axes=arc_arc, grid_spacing= 5 * u.deg, color='black') 

    # Defien the new axes for pix-pix contour.
    pix_pix = fig.add_axes(arc_arc.get_position(), frameon=False)

    # Umbra plot
    contour_plot(contour[0], ax = pix_pix, color='royalblue', font_color='royalblue')

    # Penumbra plot
    contour_plot(contour[1], ax = pix_pix, color='aliceblue', font_color='aliceblue')

    # Add colour bar.
    cb(ax = arc_arc, im = im, sub = sub)

    # Image axes setup
    im_axes(ax = arc_arc)

    # Contour axes etup
    co_axes(ax = pix_pix, im = im, sub = sub)

    # Defint output path and Filename
    path, filename = path_define(date = sub.date, AR_summary = AR_summary, obs_type = obs_type)

    # Create folder if it not exist
    os.system('mkdir -p' + ' ' + path)

    # Save
    plt.savefig(path + filename, bbox_inches='tight', facecolor="#eff0f4", edgecolor='#535353')

    return 0
