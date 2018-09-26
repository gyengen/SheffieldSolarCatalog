import numpy as np
import h5py


def PFFF(bz, nz = 30, zscale = 1, finite_energy = True):

    """Computes the linear force-free field (constant alpha). The magnetic
    field input must alreadcleary have the 180 degree ambiguity resolved.
    Uses the FFT equations from Gary, ApJ, 69, 323, 1989. By default the
    solution is NOT restricted to finite energy. This can be overcome with
    the /finite_energy keyword.

    Written by T. Metcalf 1/31/92
    30-Jul-93 TRM Fixed a bug in the computation of the FFT frequencies
    30-Oct-16 The Python implementation made by Norbert Gyenge.

    Parameters
    ----------
    bz: numpy.ndarray
        Vertical or longitudinal magnetic field. 2d array.

    nz: int
        Number of equally spaced grid points in the z direction
        (default = 30)

    zscale : int
        Sets the z-scale (1.0 = same scale as the x,y axes before the
        heliographic transformation). Default= 1.0

    finite_energy: bool

    Returns
    -------
    magout : numpy.ndarray
        New magnetic field structure with the fields bxp,byp,bzp defined
        These are 3D arrays in x,y,z giving the x,y,z components of the
        force free field.

    References
    ----------
    Gary, ApJ, 69, 323, 1989"""

    # Dimension of the region of interest.

    nys, nxs = np.shape(bz)

    # These will hold the force-free field

    bxp = np.zeros([nz, nys, nxs], dtype=float)
    byp = np.zeros([nz, nys, nxs], dtype=float)
    bzp = np.zeros([nz, nys, nxs], dtype=float)

    # The Fourier variables

    u = np.zeros([nys, nxs], dtype=float)
    v = np.zeros([nys, nxs], dtype=float)

    # Compute the Fourier frequencies (cycles per pixel)

    t = np.arange(nxs) / float(nxs)
    nn = nxs // 2
    t[nn+1:nxs] = t[nn+1:nxs] - 1

    for j in range(0, nys):
        u[:][j] = t

    t = np.arange(nys) / float(nys)
    nn = nys // 2
    t[nn+1:nys] = t[nn+1:nys] - 1

    v = v.T
    for j in range(0, nxs):
        v[:][j] = t
    v = v.T

    den = 2 * np.pi * (np.power(u, 2) + np.power(v, 2))
    den[0, 0] = 1
    overden = 1 / den

    fz = np.fft.fft2(bz) / bz.size
    fx = np.fft.fft2(bxp[:][:][0]) / bxp.size
    fy = np.fft.fft2(byp[:][:][0]) / byp.size

    # The condition that the net flux is zero
    fz[0, 0] = complex(0, 0)

    k = 4 * np.pi * np.pi * (np.power(u, 2) + np.power(v, 2))

    good = np.where(k >= 0)
    bad = np.where(k < 5)
    countg = (k >= 0).sum()
    countb = (k < 0).sum()

    k = k + (1j * np.zeros(np.shape(k)))
    cff = complex(0, 1) * 2 * np.pi / (np.sqrt(-1 * np.ndarray.flatten(k)[1:]))
    e1 = -1 * cff[1:]
    e2 = np.ndarray.flatten(u)[1:] * np.ndarray.flatten(fx)[1:]
    e3 = np.ndarray.flatten(v)[1:] * np.ndarray.flatten(fy)[1:]
    e4 = np.ndarray.flatten(fz)[1:]
    cff = e1 * (e2[:-1] + e3[:-1]) / e4[:-1]
    cff = cff.real

    if countb > 0:
        cff = np.median(cff[countb])
    else:
        cff = 0

    a1 = (1.0 + complex(0.0, 1.0) * cff) / 2.0
    a2 = (1.0 - complex(0.0, 1.0) * cff) / 2.0

    k = np.sqrt(k)



    if (countg > 0 or finite_energy == False):
        for iz in range(0, nz):

            f = np.zeros((nys, nxs), dtype=np.complex_)
            z = zscale * float(iz)

            f = -1 * complex(0, 1) * (k * u) * fz * np.exp(-1 * k * z) * overden

            if countb > 0:
                if finite_energy:
                    f[bad] = complex(0, 0)
                else:
                    f2 = -1 * complex(0, 1) * (-1 * k * u) * fz * np.exp(k * z) * overden
                    f[bad] = a1[bad] * f[bad] + a2[bad] * f2[bad]
            
            bxp[:][:][iz] = (np.fft.ifft2(f) * f.size)

            f = -1 * complex(0, 1) * (k * v) * fz * np.exp(-1 * k * z) * overden
            
            if countb > 0:
                if finite_energy:
                    f[bad] = complex(0, 0)
                else:
                    f2 = -1 * complex(0, 1) * (-1 * k * v) * fz * np.exp(k * z) * overden
                    f[bad] = a1[bad] * f[bad] + a2[bad] * f2[bad]

            byp[:][:][iz] = (np.fft.ifft2(f) * f.size)

            f = fz * np.exp(-1 * k * z)

            if countb > 0:
                if finite_energy:
                    if iz != 0:
                        f[bad] = complex(0.)
                else:
                    f2 = fz * np.exp(k * z)
                    f[bad] = a1[bad] * f[bad] + a2[bad] * f2[bad]

            bzp[:][:][iz] = (np.fft.ifft2(f) * f.size)

    return {'Bx': bxp, 'By': byp, 'Bz': bzp, 'Grid_points': nz, 'Z_scale' : zscale, 'Finite_energy' : finite_energy}


def generate_hdf5(cube, noaa, date):

    import os
    cwd = os.getcwd()

    print(cwd)

    rnd = np.random.random_integers(100, 999)
    path = 'web/temp/'
    filename = noaa + '_' + date + '_s' + str(rnd) + '.h5'
    hf = h5py.File(path + filename, 'w')
    hf.create_dataset('Bx', data=cube['Bx'])
    hf.create_dataset('By', data=cube['By'])
    hf.create_dataset('Bz', data=cube['Bz'])
    hf.close()

    return path, filename
