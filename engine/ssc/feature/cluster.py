import numpy as np
import matplotlib.pyplot as plt
from skimage import measure
from sklearn.cluster import DBSCAN
from sklearn import metrics
from sklearn.datasets.samples_generator import make_blobs
from sklearn.preprocessing import StandardScaler

def PolyArea(x,y):
    
    '''The (signed) area of a planar non-self-intersecting polygon with vertices (x_1,y_1), ...,  (x_n,y_n) is
    A=1/2(x_1y_2-x_2y_1+x_2y_3-x_3y_2+...+x_(n-1)y_n-x_ny_(n-1)+x_ny_1-x_1y_n).

    Parameters
    ----------
        x, y - Polygon points

    Returns
    -------
        Polygon area. Note that the area of a convex polygon is defined to be positive if the points
        are arranged in a counterclockwise order,and negative if they are in clockwise order (Beyer 1987).'''
    
    import numpy as np
    return 0.5*(np.dot(x,np.roll(y,1))-np.dot(y,np.roll(x,1)))

def Plot_Sunspot_Groups_Clustering(X, labels, core_samples_mask, n_clusters_):
    '''This method creates a visualisation of the result of the DBSCAN algorithm.
    '''
    unique_labels = set(labels)
    colors = plt.cm.Spectral(np.linspace(0, 1, len(unique_labels)))
    for k, col in zip(unique_labels, colors):
        class_member_mask = (labels == k)

        xy = X[class_member_mask & core_samples_mask]
        plt.plot(xy[:, 0], xy[:, 1], 'o', markerfacecolor=col, markeredgecolor='k', markersize=14)

        xy = X[class_member_mask & ~core_samples_mask]
        plt.plot(xy[:, 0], xy[:, 1], 'o', markerfacecolor=col, markeredgecolor='k', markersize=6)

    plt.title('Estimated number of clusters: %d' % n_clusters_)
    plt.show()
    return None

def Sunspot_Groups_Clustering(observation, th, mpix):
    '''
    The DBSCAN algorithm views clusters as areas of high density separated by areas of low density.
    This muthod creates sunspot groups from individual sunspots and estimates the position of 
    the groups.

    Parameters
    ----------
        observation - 2d numpy array, scaled and normalised continuum image
        th - threshold
        mpix - minimum pixel of sunspot

    Returns
    -------
        cluster_centre[i][0] - x position of the i-th cluster
        cluster_centre[i][1] - y position of the i-th cluster
        cluster_centre[i][2] - lenght of the i-th cluster

    Reference
    ---------
        Ester, M., H. P. Kriegel, J. Sander, and X. Xu, AAAI Press, pp. 226-231. 1996
    '''

    # Create an initial sunspot identification based on intensitivity.
    # Contour the individual spots.
    contours = measure.find_contours(observation, th, positive_orientation='high')

    # Create a list to store the sunspot positions.
    contour_position=[]

    # The sunspot positions is the centre of the contorus. Below mpix the contours have been neglected.
    for n, contour in enumerate(contours):
        if PolyArea(contour[:, 1], contour[:, 0]) > mpix:
            contour_position.append([np.mean(contour[:, 1]), np.mean(contour[:, 0])])

    contour_position = np.array(contour_position)

    # Standardize features by removing the mean and scaling to unit variance
    X = StandardScaler().fit_transform(contour_position)

    # Compute DBSCAN. min_samples=1 means only one spot could be a group. eps=3 is the distance 
    db = DBSCAN(min_samples=1).fit(X)
    core_samples_mask = np.zeros_like(db.labels_, dtype=bool)
    core_samples_mask[db.core_sample_indices_] = True
    labels = db.labels_

    # Number of clusters.
    n_clusters_ = len(set(labels)) - (1 if -1 in labels else 0)

    # Plot result - if you want to see what you've done...
    #Plot_Sunspot_Groups_Clustering(X, labels, core_samples_mask, n_clusters_)
    
    # Calculate the average cluster position 
    unique_labels = set(labels)
    cluster_centre=np.empty([n_clusters_, 3])

    for k in unique_labels:
        class_member_mask = (labels == k)
        group = contour_position[class_member_mask & core_samples_mask]
        cluster_centre[k][0] = int(np.average(group[:,0]))
        cluster_centre[k][1] = int(np.average(group[:,1]))
        cluster_centre[k][2] = int(np.sqrt(pow(np.max(group[:,0]) - np.min(group[:,0]), 2) + pow(np.max(group[:,1]) - np.min(group[:,1]), 2)))

    return cluster_centre
