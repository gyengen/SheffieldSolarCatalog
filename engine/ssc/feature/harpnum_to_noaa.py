import urllib.request

def harp_noaa(HARPNUM):

    ''' Converts HARPNUM to NOAA number.

    Attempts to downloads the latest sharp to noaa text file. If fails, the continues.
    The HARPNUM to NOAA file is opened and finds the NOAA number paired with the
    HARPNUM.

    Parameters
    ----------
        HARPNUM - Sharp number

    Return
    ------
    	noaa - Desired NOAA number paired with HARPNUM
    '''

    # Attempts to download latest HARPNUM to NOAA comparison file
    print ("Downloading HARP number to NOAA text file")
    url = "http://jsoc.stanford.edu/doc/data/hmi/harpnum_to_noaa/all_harps_with_noaa_ars.txt"
    try:
        urllib.request.urlretrieve(url, "data/Harpnum_to_noaa/harpnoaa.txt")
    except urllib.error.URLError:
        print ("Download failed due to urllib.error.URLError. Is there internet? Continuing")
        pass

    # Opens file and store data onto varible
    file = open('data/Harpnum_to_noaa/harpnoaa.txt', 'r')
    harpdata = file.readlines()

    # Iterating through the file in a decending order to find if the HARPNUM exists,
    # if not then set as 'n/a', otherwise set as the NOAA number paired with it
    max = len(harpdata)-1
    HARPNUM = int(HARPNUM) # Easier to handle HARPNUM as a integer.

    for i in range(max):
        harpstr = harpdata[max-i]
        harp = str.split(harpstr) # Split string into a list with two items - HARPNUM and NOAA
        if int(harp[0]) < HARPNUM: # Loop has gone past HARPNUM - Break
            noaa = 'N/A'
            break
        elif int(harp[0]) == HARPNUM: # Loop has found matching NOAA number
            noaa = harp[1]
            break
        else:
            continue
    return noaa
