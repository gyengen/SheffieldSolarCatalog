from datetime import timedelta, datetime
from pathlib import Path
import sunpy.map
import drms
import pyfits


def real_time_service(lag):
    '''The function defines the name of the downloadable observation.

    Parameters
    ----------
        lag - The time difference between the date of observation and
        the date of engine start

    Returns
    -------
        String - The name of the observation'''

    # Define the date of the observation
    sd = datetime.today() - timedelta(days=lag)

    # Date format conversion
    YMD = sd.strftime("%Y") + '.' + sd.strftime("%m") + '.' + sd.strftime("%d")

    # Create the name of the observation
    observation_date = YMD + '_' + sd.strftime("%H") + ':' + sd.strftime("%M")

    return observation_date


def drms_query(query, email, path):
    '''This module sends the query to the JSOC server and starts the downloand.

    Parameters
    ----------
        query - Query strint to the JSOC server
        email - The registred email address

    Returns
    -------
        The filename of the downloaded file with absolute path'''

    # Logging into JSOC database and requesting files
    client = drms.Client(verbose=False)

    # Send the Query
    q = client.export(query, method='url_quick', protocol='fits', email=email)

    # Downloading the images.
    obs = q.download(path)

    return obs


def get_sharp(date_of_obs, interval, email):

    '''This module download the Sharp data.

    Parameters
    ----------
        interval - Temporal resolution of the requested data
        date - The date of observation

    Returns
    -------
        raw_sharp - raw_sharp sunpy maps'''

    # Define the path
    path = str(Path(__file__).parent.parent) + '/web/static/data/AR/'

    # Name of the series
    series = 'hmi.Mharp_720s'
    # query_string used to search for file
    # Want query_string to look like 'Mharp_720s[]2018.05.06_TAI/12m@12m'
    q = series + '[]' + '[' + date_of_obs + '_TAI/' + interval +']' + '{bitmap}'

    try:
        # Save the filename and path
        file_list = drms_query(q, email, path)

        # Convert the Pandas dataframe to list
        file_list = file_list.loc[:]['download'].tolist()

        # Read the HARP information
        HARP=[]
        for file in file_list: HARP.append(pyfits.open(file))

        return HARP

    except:
        return False


def get_data(date_of_obs, interval, email):

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

    # Building Query string, using 45s observations
    query = ['hmi.ic_45s' + '[' + date_of_obs + '_TAI/' + interval + ']',
             'hmi.m_45s' + '[' + date_of_obs + '_TAI/' + interval + ']']

    # Define the path
    path = str(Path(__file__).parent.parent) + '/web/static/data/obs/'

    try:
        # Query and download
        file_list = []
        for q in query:

            # Download the observation and save the filename
            filename = drms_query(q, email, path)

            # Append a list of filanames
            file_list.append(str(filename.loc[0]['download']))

        # Loading observations. This is done as the downloading variable
        # contains a table with data
        observations = sunpy.map.Map(file_list)

        return observations

    except:
        return False

