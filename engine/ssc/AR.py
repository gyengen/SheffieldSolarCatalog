'''----------------------------------------------------------------------------

AR.py



----------------------------------------------------------------------------'''


import matplotlib.pyplot as plt
from astropy import units as u
import engine.ssc.sunspot.coordinates as coor
import matplotlib.cm as mcm
from astropy.io import fits
import engine.ssc.sunspot.pixel as pix
import engine.ssc.sunspot.area as area
import engine.ssc.sunspot.sql as sql
import engine.ssc.tools.util as util
import sunpy.cm as scm
import numpy as np


__author__ = "Norbert Gyenge"
__email__ = "n.g.gyenge@sheffield.ac.uk"


class Sunspot_groups(object):
    NOAA = []
    SC = []
    ROI = []
    HG_mask = []

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
        fname = util.fname(str(sub.date).split('.')[0],
                           self.obs_type, self.NOAA, 'fits')

        # Submap, focused on the region of interest
        data = np.array(sub.data, dtype=float)

        # Separate umbra and penumbra data
        for ctype in ['umbra', 'penumbra']:

            if ctype is 'umbra':

                # The coordinates of the umbra
                sunspots = self.SC[0]

                # Create the initial umbra mask
                umbra_mask = np.zeros(np.shape(self.MASK[0]), dtype=int)

            if ctype is 'penumbra':

                # The coordinates of the penumbra
                sunspots = self.SC[1]

                # create the initial penumbra mask
                penumbra_mask = np.zeros(np.shape(self.MASK[1]), dtype=int)

            # Loop over the individual sunspots
            for i, spot_position in enumerate(sunspots):

                # Extract the x and y coordinates of the sunspot
                x = spot_position[1]
                y = spot_position[0]

                # Create a dictionary from the data
                spot = pix.spot_grid(sub, x, y)

                # The background is zero
                spot = np.where(spot != 0, i + 1, 0)

                # Append the umbra mask, every spot has an id number
                if ctype is 'umbra':
                    umbra_mask = umbra_mask + spot

                # Append the penumbra mask
                if ctype is 'penumbra':
                    penumbra_mask = penumbra_mask + spot

        # Create the fits header first
        hdr = fits.Header()

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
                hdr[key] = value

        # Additional fields, the associated NOAA number and source
        hdr['source'] = 'Sheffield Solar Catalog'
        hdr['NOAA'] = self.NOAA

        # Bottom Left corner of ROI, x- and y-coordinates
        hdr['bl_x'] = self.ROI[0][0]
        hdr['bl_y'] = self.ROI[0][1]

        # Top Right corner of ROI, x- and y-coordinates
        hdr['tr_x'] = self.ROI[1][0]
        hdr['tr_y'] = self.ROI[1][1]

        if len(self.HG_mask) == 2:
            # Define the hdu list, header, image and the masks
            hl = [fits.PrimaryHDU(header=hdr, data=data),
                  fits.ImageHDU(data=np.array(umbra_mask, dtype=np.uint16)),
                  fits.ImageHDU(data=np.array(penumbra_mask, dtype=np.uint16)),
                  fits.ImageHDU(data=np.array(self.HG_mask[0], dtype=np.float32)),
                  fits.ImageHDU(data=np.array(self.HG_mask[1], dtype=np.float32))]

            # Create the HDU list
            hdu = fits.HDUList(hl)

            # Write the fits
            hdu.writeto(fname, overwrite=True, output_verify='silentfix')

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
        file_name = util.fname(date, self.obs_type, self.NOAA, 'png')
        plt.savefig(file_name, bbox_inches='tight', dpi=100)

        # Tight layout and save pdf figure
        file_name = util.fname(date, self.obs_type, self.NOAA, 'pdf')
        plt.savefig(file_name, bbox_inches='tight', dpi=600)
        plt.close()

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
                spot = pix.spot_grid(sub, x, y)
                sm = np.where(spot != 0, 1, 0)

                # Save the date
                date = [str(self.img.date).split()[0],
                        str(self.img.date).split()[1].split('.')[0]]

                # Reorder the coordinates for the area and coordinate functions
                rx = (self.ROI[0][0], self.ROI[1][0]) * u.pixel
                ry = (self.ROI[0][1], self.ROI[1][1]) * u.pixel

                # Estimate the area
                a, self.HG_mask = area.AreaC(self.img, rx, ry, sm)

                # Calculate the spot's coordinate
                c = coor.Sunspot_coord(self.img, rx, ry, sm)

                # Calculate the photon flux
                p = pix.Data_statistic(spot)

                # Concatenation the data and return
                row = sql.create_row(i, self.NOAA,[self.obs_type, ctype],
                                     date, a, c, p)

                # Append the sql database with the new row of data
                sql.sunspot_continuum_table(row)

