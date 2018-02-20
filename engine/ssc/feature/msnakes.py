from matplotlib import pyplot as ppl
import numpy as np
import morphsnakes
import scipy


__author__ = "Norbert Gyenge"
__email__  = "n.g.gyenge@sheffield.ac.uk"


def Morphological_Snakes_mask(sub, TH):
    ''' Create a binary map from the active region.

    Parameters
    ----------
        sub - Sunpy submap of the active region
        TH - Threshold

    Returns
    -------
        ini - binary mask of the active region (if img > TH then 1 else 0), same region as AR_cut'''

    return np.where(sub > TH, 1, 0)

def Morphological_Snakes(AR_cut, ini):
    '''This function is calling the 'morphsnakes' library.
    You can find more info here: https://github.com/pmneila/morphsnakes

    Parameters
    ----------
        AR_cut - Sunpy submap of the active region
        ini - binary mask of the active region (if img > TH then 1 else 0), same region as AR_cut

    Returns
    -------
        result[0] - penumbra mask
        result[1] - umbra mask

    References
    ----------
        1) Marquez-Neila, P., Baumela, L., Alvarez, L., A morphological approach
        to curvature-based evolution of curves and surfaces. IEEE Transactions
        on Pattern Analysis and Machine Intelligence (PAMI), 2013.

        2) A morphological approach to curvature-based evolution of curves and surfaces.
        Pablo Marquez-Neila, Luis Baumela, Luis Alvarez. In IEEE Transactions on Pattern Analysis
        and Machine Intelligence (PAMI).

        3) Morphological Snakes. Luis Alvarez, Luis Baumela, Pablo Marquez-Neila. In Proceedings
        of the IEEE Conference on Computer Vision and Pattern Recognition 2010 (CVPR10).'''

    # Penumbra first
    gI = morphsnakes.gborders(AR_cut, alpha=1, sigma=1)
    macwe = morphsnakes.MorphACWE(AR_cut, smoothing=0, lambda1=1, lambda2=10)

    # Initial condition of the Morphological_Snakes method
    macwe.levelset = ini

    # Use this line if you want to see the evolution of the contour
    #morphsnakes.evolve_visual(macwe, num_iters=100, background=AR_cut)

    # Finding the best contour
    for i in range(100):
        macwe.step()

    # Save the result
    penumbra_mask = macwe.levelset

    # Umbra
    gI = morphsnakes.gborders(AR_cut, alpha=1, sigma=1)
    macwe = morphsnakes.MorphACWE(AR_cut, smoothing=0, lambda1=10, lambda2=1)

    # Initial condition of the Morphological_Snakes method
    macwe.levelset = ini

    # Use this line if you want to see the evolution of the contour
    #morphsnakes.evolve_visual(macwe, num_iters=100, background=AR_cut)

    # Finding the best contour
    for i in range(100):
        macwe.step()

    # Save the result
    umbra_mask = macwe.levelset

    return [penumbra_mask, umbra_mask]
