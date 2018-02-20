import numpy as np
from astropy.table import Table, Column

def NOAA(cluster_centre, AR):
    '''Associate the cluster cores with active regions defined by NOAA.
    Define the center of the clusters and define the region of interest (box size).

    Parameters
    ----------
        cluster_centre - x,y coordinates of the cluster centre and the size of the cluster
        AR - SRS table

    Returns
    -------
        AR - SRS table with updated coordinates.'''

    # Define the number of the features.
    number_of_cluster_cores = len(cluster_centre)
    number_of_NOAA_active_regions = len(AR)

    # The minimum box size and aspect ration (16:9)
    min_box_size = 150
    aspect_ratio = 0.5625

    # Create two new column for storing the dimensions of the region of sunspot group 
    AR.add_column(Column(np.zeros(len(AR)), name='dx'), index=6)
    AR.add_column(Column(np.zeros(len(AR)), name='dy'), index=6)

    # Find the closest distance between the NOAA AR position and the cluster position.
    # Associate the clusters and NOAA numbers and it is done.

    if number_of_cluster_cores >= number_of_NOAA_active_regions:
        for i in range(len(AR)):
            # Calculate the distance between the unnamed and named clusters.
            dist = np.sqrt(pow((cluster_centre[:, 1] - AR['Y'][i]), 2) + pow((cluster_centre[:, 0] - AR['X'][i]), 2))

            # Choose the closest cluster.
            index = np.where(dist==np.partition(dist, 0)[0])

            # Overwrite SRS table with the new coordinates.
            AR['X'][i], AR['Y'][i], = cluster_centre[index, 0], cluster_centre[index, 1]

            # Define the region of interest. 0.5625 means, aspect ratio equals to 16:9
            AR['dx'][i], AR['dy'][i] = cluster_centre[index, 2], (cluster_centre[index, 2] * aspect_ratio)

            # The minimal horizontal dimension of box size must be greater than min_box_size
            if AR['dx'][i] < min_box_size : AR['dx'][i], AR['dy'][i] = min_box_size, (min_box_size * aspect_ratio)

        # 1st possibility: Number of cluster cores == Number of cluster cores. Job is done. 
        if number_of_cluster_cores == number_of_NOAA_active_regions:return AR

        # 2nd possibility: Number of cluster cores > Number of cluster cores
        # Create a new NOAA identification for the missing cluster.
        if number_of_cluster_cores > number_of_NOAA_active_regions:
            
            # Select the unnamed clusters.
            unidentified_cluster_x = np.setdiff1d(np.array(cluster_centre[:, 0]), np.array(AR['X']))
            unidentified_cluster_y = np.setdiff1d(np.array(cluster_centre[:, 1]), np.array(AR['Y']))

            # Iterate over the unnamed cluster(s)
            for i, (x, y) in enumerate(zip(unidentified_cluster_x, unidentified_cluster_y)):
                # Calculate the distance between the unnamed and named clusters.
                dist = np.sqrt(pow((cluster_centre[:, 1] - y), 2) + pow((cluster_centre[:, 0] - x), 2))

                # Choose the closest named cluster.
                index = np.where(dist==np.partition(dist, 1)[1])
                
                # A suffix will be added for the name of every new spot. 
                suffix = map(chr, range(97, 123))[i]

                # Add the new cluster to the SRS table
                AR.add_row(np.zeros(len(AR[0])))

                # Create a name for the new cluster. The new name refers to the closest sunspot group.
                AR['Nmbr'][-1] = AR['Nmbr'][index[0][0]]

                # Save the coordinates and the dimensions of region of interest of the cluster centre
                AR['X'][-1], AR['Y'][-1]  = x, y
                AR['dx'][-1], AR['dy'][-1] = min_box_size, (min_box_size * aspect_ratio)

                # We have no magnetic classification for the nem active region. Probably NOAA missed just a unipolar little spot.
                AR['Z'][-1], AR['Mag_Type'][-1] = 'N/A', 'Unnamed'

                # The suffix distinguishes between the new spot and the closest one.
                AR['Location'][-1] = suffix

            return AR
