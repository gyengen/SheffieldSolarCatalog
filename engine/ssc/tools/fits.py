'''----------------------------------------------------------------------------

plot.py



----------------------------------------------------------------------------'''

from astropy.io import fits
import scipy.ndimage
import engine.ssc.tools.util as util
import numpy as np

__author__ = "Norbert Gyenge"
__email__ = "n.g.gyenge@sheffield.ac.uk"


def HMI_full_disk_fits(Active_Regions, img, scale):

    bl_x, bl_y = [], []
    tl_x, tl_y = [], []
    NOAA = []

    # Loop over each sunspot groups
    for AR in Active_Regions:

        # Define the ROI
        bl_x.append(str(int(AR.ROI[0][0] * scale)))
        bl_y.append(str(int(AR.ROI[0][1] * scale)))
        tl_x.append(str(int(AR.ROI[1][0] * scale)))
        tl_y.append(str(int(AR.ROI[1][1] * scale)))

        # Add the NOAA number at the corner of the box
        NOAA.append(str(AR.NOAA))

    # Create the fits header first
    hdr = fits.Header()

    # Start to fill the header
    for key, value in img.meta.items():

        # Define out the unnecessary fields
        skip = ['xtension', 'source', 'keycomments',
                'lutquery', 'distcoef', 'rotcoef',
                'codever0', 'codever1', 'codever2',
                'codever3', 'history', 'comment', 'blank']

        # Filter out the unnecessary fields
        bad_header = key in skip

        # Add the useful elements to the header
        if bad_header is not True:
            hdr[key] = value

    # Define the custom header records
    hdr['source'] = 'Sheffield Solar Catalogue'

    # Generate a list of active regions, ROI
    hdr['ARs'] = ",".join(NOAA)

    # Generate a list of position of ROI corner
    hdr['bl_x'] = ",".join(bl_x)
    hdr['bl_y'] = ",".join(bl_y)
    hdr['tr_x'] = ",".join(tl_x)
    hdr['tr_y'] = ",".join(tl_y)

    # Scale few variables
    hdr['CRPIX1'] = str(int(int(hdr['CRPIX1']) * scale))
    hdr['CRPIX2'] = str(int(int(hdr['CRPIX2']) * scale))
    hdr['CDELT1'] = str(float(hdr['CDELT1']) / scale)
    hdr['CDELT2'] = str(float(hdr['CDELT2']) / scale)

    # Save the scale value
    hdr['scale'] = str(scale)

    # Define the path and file name, vector graphics output first
    fname = util.fname(str(img.date).split('.')[0],
                       img.measurement, 'fulldisk', 'fits')

    # Initialise the image data
    data = np.array(img.data)

    # Replace the nan's in the image
    data = np.where(np.isnan(data), np.nanmin(data), data)

    # Reshape the data
    data = scipy.ndimage.zoom(data, scale, order=0)

    # Write the fits
    fits.writeto(fname, data=data, header=hdr, overwrite=True)

    return
