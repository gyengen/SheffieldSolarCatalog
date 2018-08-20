'''----------------------------------------------------------------------------

AR.py



----------------------------------------------------------------------------'''


import matplotlib.pyplot as plt
from astropy import units as u
import ssc.sunspot.coordinates
import matplotlib.cm as mcm
import ssc.sunspot.pixel
import ssc.sunspot.area
import ssc.sunspot.sql
import ssc.tools.util
import sunpy.cm as scm
import numpy as np
import pyfits

__author__ = "Norbert Gyenge"
__email__ = "n.g.gyenge@sheffield.ac.uk"


class Sunspot_groups(object):
    NOAA = []
    SC = []
    ROI = []

    def __init__(self, NOAA, MASK, SC, ROI):
        self.NOAA = NOAA
        self.SC = SC
        self.ROI = ROI
        self.MASK = MASK

    def input(self, img, obs_type):
        self.img = img
        self.obs_type = obs_type

    def savefits(self):

        # Cut the ROI
        sub = self.img.submap(self.ROI[0] * u.pixel, self.ROI[1] * u.pixel)

        # Define the filename the
        fname = ssc.tools.util.fname(str(sub.date).split('.')[0],
                                     self.obs_type, self.NOAA, 'fits')

        # Create the HDU, containing the observation
        img = pyfits.PrimaryHDU()

        # Submap, focused on the region of interest
        img.data = sub.data

        # Start to fill the header
        for key, value in sub.meta.items():

            # Define out the unnecessary fields
            skip = ['xtension', 'source', 'keycomments',
                    'lutquery', 'distcoef', 'rotcoef',
                    'codever0', 'codever1', 'codever2',
                    'codever3', 'history', 'comment']

            # Filter out the unnecessary fields
            bad_header = key in skip

            # Add the useful elements to the header
            if bad_header is not True:
                img.header[key] = value

        # Additional fields, the associated NOAA number and source
        img.header['source'] = 'Sheffield Solar Catalouge'
        img.header['NOAA'] = self.NOAA

        # Bottom Left corner of ROI, x- and y-coordinates
        img.header['bl_x'] = self.ROI[0][0]
        img.header['bl_y'] = self.ROI[0][1]

        # Top Right corner of ROI, x- and y-coordinates
        img.header['tr_x'] = self.ROI[1][0]
        img.header['tr_y'] = self.ROI[1][1]

        # Submap mask, same dimension as img
        contour_mask = np.dstack((self.MASK[0], self.MASK[1]))

        # Create the 3D cube
        img.data = np.dstack((img.data, contour_mask))

        # Rotationg the 3D cube, x- and y- dimension should be
        # Solar-X and Solar-Y and z-dimension represent the layers
        img.data = np.transpose(img.data, (2, 0, 1))

        img.writeto(fname, clobber=True)

    def save(self):

        if self.obs_type == 'continuum':
            cmap = scm.get_cmap(name='yohkohsxtal')
            color = 'k'

        elif self.obs_type == 'magnetogram':
            cmap = mcm.Greys
            color = 'w'

        # Cut the ROI
        sub = self.img.submap(self.ROI[0] * u.pixel, self.ROI[1] * u.pixel)

        # Plot the figure
        plt.figure(figsize=(8, 6))

        # Plotting the real observation first
        sub.plot(cmap=cmap)

        # No grid, yes limb
        plt.grid(False)
        sub.draw_limb(lw=0.5, color=color)

        # Add a overlay grid.
        sub.draw_grid(grid_spacing=5 * u.deg, color=color)

        # Plot the penumbra contours
        for i, spot_position in enumerate(self.SC[0]):
            plt.plot(spot_position[1], spot_position[0], color='b', lw=1)

        # Plot the umbra contours
        for i, spot_position in enumerate(self.SC[1]):
            plt.plot(spot_position[1], spot_position[0], color='w', lw=1)

        # Add watermark, position bottom right
        plt.annotate('SSC', xy=(0.9, 0.05), fontsize=10, color='k',
                     xycoords='axes fraction', alpha=0.5)

        # Save the date
        date = str(sub.date).split('.')[0]

        # Tight layout and save pdf figure
        file_name = ssc.tools.util.fname(date, self.obs_type, self.NOAA, 'png')
        plt.savefig(file_name, bbox_inches='tight', dpi=100)

        # Tight layout and save pdf figure
        file_name = ssc.tools.util.fname(date, self.obs_type, self.NOAA, 'pdf')
        plt.savefig(file_name, bbox_inches='tight', dpi=600)

    def append_sql(self):

        # Cut the ROI
        sub = self.img.submap(self.ROI[0] * u.pixel, self.ROI[1] * u.pixel)

        # Separate umbra and penumbra data
        for ctype in ['umbra', 'penumbra']:

            if ctype is 'umbra':
                sunspots = self.SC[0]

            if ctype is 'penumbra':
                sunspots = self.SC[1]

            # Cut the ROI
            sub = self.img.submap(self.ROI[0] * u.pixel, self.ROI[1] * u.pixel)

            # Loop over the individual sunspots

            for i, spot_position in enumerate(sunspots):

                # Extract the x and y coordinates of the sunspot
                x = spot_position[1]
                y = spot_position[0]

                # Create a dictionary from the data
                spot = ssc.sunspot.pixel.spot_grid(sub, x, y)
                sm = np.where(spot != 0, 1, 0)

                # Save the date
                date = [str(self.img.date).split()[0],
                        str(self.img.date).split()[1].split('.')[0]]

                # Reorder the coordinates for the area and coordinate functions
                rx = (self.ROI[0][0], self.ROI[1][0]) * u.pixel
                ry = (self.ROI[0][1], self.ROI[1][1]) * u.pixel

                # Estimate the area
                a = ssc.sunspot.area.Area_Calculation(self.img, rx, ry, sm)

                # Calculate the spot's coordinate
                c = ssc.sunspot.coordinates.Sunspot_coord(self.img, rx, ry, sm)

                # Calculate the photon flux
                p = ssc.sunspot.pixel.Data_statistic(spot)

                # Concatenation the data and return
                row = ssc.sunspot.sql.create_row(i, self.NOAA,
                                                 [self.obs_type, ctype],
                                                 date, a, c, p)

                # Append the sql database with the new row of data
                ssc.sunspot.sql.sunspot_continuum_table(row)