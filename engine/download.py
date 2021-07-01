from datetime import timedelta, datetime
import astropy.io.fits as pyfits
from pathlib import Path
import multiprocessing
import itertools
import sunpy.map
import drms


def cadance():
    ''' Define the observation cadance. Min cadance is 60 minutes and 
    Max cadance is 1 minute.

    Parameters
    ----------
        step - int: in minutes or hours. This number will be divided by 
            the number of cores.

    Returns
    -------
        int - cadance'''


    # Define core number, -1 for the web interface
    cores = multiprocessing.cpu_count()

    # Define max and min cadance
    if cores > 1:
        cores = cores - 1

    if cores > 60:
        cores = 60

    return str(int(60 / cores))


def date_convert(date_in, lag):
    '''The function defines the name of the downloadable observation.

    Parameters
    ----------
        lag - The time difference between the date of observation and
        the date of engine start,
            False: Service is not real time 

    Returns
    -------
        String - The name of the observation'''

    # Define the date of the observation

    if lag:
        x = datetime.today() - timedelta(days=lag)

    else:
        x = date_in

    # Create the name of the observation
    return x.strftime("%Y") + '.' + x.strftime("%m") + '.' + x.strftime("%d") + '_' + x.strftime("%H") + ':' + x.strftime("%M") + ':00'


def get_sharp(date_of_obs, lag=False):

    '''This module download the Sharp data.

    Parameters
    ----------
        interval - Temporal resolution of the requested data
        date - The date of observation

    Returns
    -------
        raw_sharp - raw_sharp sunpy maps'''

    date_of_obs = date_convert(date_of_obs, lag)

    # Define the path
    path = str(Path(__file__).parent.parent) + '/web/static/data/AR/'

    # Name of the series
    series = 'hmi.Mharp_720s'

    # query_string used to search for file
    # Want query_string to look like 'hmi.Mharp_720s[]2018.05.06_TAI/12m@12m'
    s_query = series + '[]' + '[' + date_of_obs + '_TAI/' + '12m@12m' +']' + '{bitmap}'

    # Logging into JSOC database and requesting files
    c_sharp = drms.Client(verbose=False)

    # Send the Query
    req_sa = c_sharp.export(s_query, method='url_quick',protocol='fits', email='scc@sheffield.ac.uk')

    req_sa.wait(timeout=None, sleep=10, retries_notfound=60, verbose=False)

    # Save the filename and path
    file_list = req_sa.download(path)

    # Convert the Pandas dataframe to list
    file_list = file_list.loc[:]['download'].tolist()

    try:

        # Read the HARP information
        return [pyfits.open(file) for file in file_list]

    except Exception:

        return False


def get_data(date_of_obs, lag=False):

    '''

    Parameters
    ----------
        - Date
        - Interval
        - Email

    Returns
    -------
        observations - Sunpy map object

    Notes
    ------

    Observation downloading and loading module.
    The DRMS module requires a query string to search for the desired
    observation files. The first half of the function is used to create
    a varible query string and the second half downloads the observations
    using the query string. The last line loads the observation files.
    This is done as the downloading variable produces a table containing
    the location of the downloaded files and this can be used to load the
    observation files for convenience. Example query strings are,

    'Series'+'Year.Month.Day'+'_'+'Hour:Minute:Second'+'_TAI/'+interval

    Note that the hour:minute:second does not need to be specified and
    defaults to midnight. Currently downloading Continuum and Magnetogram
    observations.'''

    date_of_obs = date_convert(date_of_obs, lag)
    cd = cadance()

    # Building Query string, using 45s observations
    d_query = ['hmi.ic_45s' + '[' + date_of_obs + '_TAI/' + '1h@' + cd + 'm' + ']',
              'hmi.m_45s'  + '[' + date_of_obs + '_TAI/' + '1h@' + cd + 'm' + ']']

    # Define the path
    path = str(Path(__file__).parent.parent) + '/web/static/data/obs/'


    # Logging into JSOC database and requesting files
    c_data = drms.Client(verbose=False)

    # Send the Query
    req_ic = c_data.export(d_query[0], method='url_quick',
                           protocol='fits', email='n.g.gyenge@gmail.com')

    req_ic.wait(timeout=None, sleep=10, retries_notfound=60, verbose=False)

    req_ma = c_data.export(d_query[1], method='url_quick',
                           protocol='fits', email='scc@sheffield.ac.uk')

    req_ma.wait(timeout=None, sleep=10, retries_notfound=60, verbose=False)

    # Downloading the images.
    filename = [req_ic.download(path), req_ma.download(path)]

    # Reorganise observations: [[ic1, mag1], [ic2, mag2], ...]
    filename = [[filename[0]['download'][i], filename[1]['download'][i]]
                for i in range(len(filename[0]))]

    try:

        # Loading observations.
        return [sunpy.map.Map(obs) for obs in filename]

    except Exception: 

        return False
