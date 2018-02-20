from astropy import units as u
from skimage import measure
import numpy as np


def Morphological_Snakes_contours(AR_mask, min_pixel_size):
    '''Create contours from a binary mask. The binary mask contains all the spots in one matrix.
    In this procedure we define the individal spots by different contours (polygon).
    The binary mask must is produced by the Morphological_Snakes procedure.

    Based on
    --------

    Lorensen, William and Harvey E. Cline. Marching Cubes: A High Resolution 3D Surface
    Construction Algorithm. Computer Graphics (SIGGRAPH 87 Proceedings) 21(4) July 1987, p. 163-170)

    Parameters
    ----------
        ms_penumbra_mask - Binary mask of penumbrae.
        ms_umbra_mask - Binary mask of umbrae.
        min_pixel_size - Spot size filter

    Returns
    -------
        result[0] - penumbra_contours
        result[1] - umbra_contours'''

    penumbra_mask = AR_mask[0]
    umbra_mask = AR_mask[1]

    # From mask to contour
    penumbra_contours = measure.find_contours(penumbra_mask , 0.5, positive_orientation='high')
    umbra_contours = measure.find_contours(umbra_mask , 0.5, positive_orientation='high')

    return [penumbra_contours, umbra_contours]

def Contours_coord_t(continuum_img, contours_up, active_region):
    ''' 

    FAILD

    Coordinate transformation of the active region meshgrid from pixels to arcsecs.

    Parameters
    ----------
        continuum_img - Sunpy map
        contours_up - spot countours by Contours_size_filter
        active_region - SRS information

    Return
    ------
        selected_umbra - arcsec mashgrid
        selected_penumbra - arcsec mashgrid'''

    # Getting the corner coordinates. x = corner[0]

    corner = continuum_img.data_to_pixel(active_region['box_x1'] * u.arcsec,
                                         active_region['box_y1'] * u.arcsec)

    selected_umbra = []
    selected_penumbra = []

    # Filter the penumbrae and umbrae data
    for i in range(2):

        # Select penumbra first, than umbra
        contours = contours_up[i]

        # Loop over the contours, every sunspot groups, every spots
        for n, contour in enumerate(contours):

            # Pix to arcsec every point of the mashgrid; x = contour[:,1]
            con = continuum_img.pixel_to_data(contour[:,1] * u.pix + corner[0],
                                              contour[:,0] * u.pix + corner[1])

            # Save the significant positive peaked spots
            if i == 0: selected_umbra.append(con)
            if i == 1: selected_penumbra.append(con)

    return [selected_umbra, selected_penumbra]

def PolyArea(x, y):

    '''The (signed) area of a planar non-self-intersecting polygon with vertices (x_1,y_1), ...,
    (x_n,y_n) is A=1/2(x_1y_2-x_2y_1+x_2y_3-x_3y_2+...+x_(n-1)y_n-x_ny_(n-1)+x_ny_1-x_1y_n).
    Note that the area of a convex polygon is defined to be positive if the points are arranged
    in a counterclockwise order, and negative if they are in clockwise order (Beyer 1987).

    Parameters
    ----------
        x, y - Polygon points

    Returns
    -------
        Polygon area.'''

    return 0.5 * (np.dot(x, np.roll(y, 1))-np.dot(y, np.roll(x, 1)))

def Contours_size_filter(contours, min_pixel_size):

    '''Contour selecting procedure. 1) The area of the feature must be larger than 'min_pixel_size'.
    2) The polygon must be positive positive. Positive polygon indicates the higher values inside of
    the feature. Negative is lower inside.

    Parameters
    ----------
        contours - Unfiltered contours
        min_pixel_size - Minimum size of sunspot in pixels.

    Returns
    -------
        selected_contours - Filtered contours'''

    selected_umbra=[]
    selected_penumbra=[]

    # Filter the penumbrae and umbrae data
    for i in range(2):

        # Select penumbra first, than umbra
        contour = contours[i]

        # Loop over the contours, every sunspot groups, every spots
        for n, con in enumerate(contour):

            # Filter the small areas and the negative peaks
            if PolyArea(con[:, 1], con[:, 0]) > min_pixel_size:

                # Save the significant positive peaked spots
                if i == 0: selected_umbra.append(con.T)
                if i == 1: selected_penumbra.append(con.T)

    return [selected_umbra, selected_penumbra]

