'''----------------------------------------------------------------------------

plot.py



----------------------------------------------------------------------------'''

from astropy.io import fits
import ssc.tools.util
import numpy as np

__author__ = "Norbert Gyenge"
__email__ = "n.g.gyenge@sheffield.ac.uk"


def HMI_full_disk_fits(Active_Regions, img):

    bl_x, bl_y = [], []
    tl_x, tl_y = [], []
    NOAA = []

    # Loop over each sunspot groups
    for AR in Active_Regions:

        # Define the ROI
        bl_x.append(str(AR.ROI[0][0]))
        bl_y.append(str(AR.ROI[0][1]))
        tl_x.append(str(AR.ROI[1][0]))
        tl_y.append(str(AR.ROI[1][1]))

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
                'codever3', 'history', 'comment']

        # Filter out the unnecessary fields
        bad_header = key in skip

        # Add the useful elements to the header
        if bad_header is not True:
            hdr[key] = value

    # Define the custom header records
    hdr['source'] = 'Sheffield Solar Catalog'

    # Generate a list of active regions, ROI
    hdr['ARs'] = ",".join(NOAA)

    # Generate a list of position of ROI corner
    hdr['bl_x'] = ",".join(bl_x)
    hdr['bl_y'] = ",".join(bl_y)
    hdr['tr_x'] = ",".join(tl_x)
    hdr['tr_y'] = ",".join(tl_y)

    # Define the path and file name, vector graphics output first
    fname = ssc.tools.util.fname(str(img.date).split('.')[0],
                                 img.measurement, 'fulldisk', 'fits')

    # Initialise the image data
    data = np.array(img.data)

    # Replace the nan's in the image
    data = np.where(np.isnan(data), np.nanmin(data), data)

    # Compress the data
    hdu = fits.CompImageHDU(header=hdr, data=np.array(data, dtype=np.float32))

    # Write the fits
    hdu.writeto(fname, overwrite=True, output_verify='silentfix')

    return
