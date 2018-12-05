import sqlite3 as s3
import os


def create_row(i, NOAA, o_type, date_time, area, co, data_stat):
    ''' Mergeing the results of the sunspot data into.

    Parameters
    ----------
        o_type - observation type and feature type array
        date_time - date and time array
        area - Results of Feature_Area_Calculation() function
        co - results of Sunspot_coordinates() function
        data_stat - Results of Data_statistic() function

     Returns
    -------
        result - Merged list without dimensions'''

    # Define keys and one element for each. One row dictionary.

    result = [date_time[0], date_time[1], o_type[0], o_type[1],
              NOAA, i + 1, co[0].value, co[1].value, co[2].value,
              co[3].value, co[4].value, co[5].value, co[6].value,
              area[0].value, area[1].value, area[2].value, data_stat[0],
              data_stat[1], data_stat[2], data_stat[3], data_stat[4]]

    return result


def create_primary_key(row):
    ''' Create a unique primary key for the sql database for each row.

    Parameter
    ---------
        row - list, includes one database row

    Returns
    -------
        primary_key - unique id

    Notes
    -----
        Abbreviations:
            Observation type first:

            continuum = 00
            magnetogram = 01

            Feature type:
            penumbra = 00
            umbra = 01
        '''

    date_p = row[0].split('-')
    time_p = row[1].split(':')

    # Data and time part
    key = date_p[0][2:] + date_p[1] + date_p[2] + '-'
    key = key + time_p[0] + time_p[1] + time_p[2] + '-'

    # Store observation type and feature information
    if str(row[2]) is 'continuum':
        key = key + '00'

    if str(row[2]) is 'magnetogram':
        key = key + '01'

    if str(row[3]) is 'penumbra':
        key = key + '00'

    if str(row[3]) is 'umbra':
        key = key + '01'

    # Add separator
    key = key + '-'

    # Store the NOAA number
    key = key + str(int(row[4]) - 10000) + '-'

    # Store the id of the feature
    if row[5] < 10:
        f_id = '00' + str(row[5])

    if row[5] >= 10 and row[5] < 100:
        f_id = '0' + str(row[5])

    if row[5] >= 100:
        f_id = str(row[5])

    primary_key = key + f_id

    return str(primary_key)


def create_sunspot_magnetogram_table(c):

    # Create table if it does not exist
    c.execute('''CREATE TABLE IF NOT EXISTS magnetogram_sunspot(
                 Date_obs DATE,
                 Time_obs TIME,
                 Obs_type VARCHAR,
                 Fea_type VARCHAR,
                 NOAA INTEGER,
                 id INTEGER,
                 X_arc FLOAT,
                 Y_arc FLOAT,
                 r_arc FLOAT,
                 theta_deg FLOAT,
                 b_deg FLOAT,
                 l_deg FLOAT,
                 lcm_deg FLOAT,
                 A_deg2 FLOAT,
                 A_MSH FLOAT,
                 A_km2 FLOAT,
                 B_Total FLOAT,
                 B_Mean FLOAT,
                 B_Min FLOAT,
                 B_Max FLOAT,
                 B_Std FLOAT,
                 p_key VARCHAR(27),
                 PRIMARY KEY(p_key)
                 );''')

    return 0


def create_sunspot_continuum_table(c):

    # Create table if it does not exist
    c.execute('''CREATE TABLE IF NOT EXISTS continuum_sunspot(
                 Date_obs DATE,
                 Time_obs TIME,
                 Obs_type VARCHAR,
                 Fea_type VARCHAR,
                 NOAA INTEGER,
                 id INTEGER,
                 X_arc FLOAT,
                 Y_arc FLOAT,
                 r_arc FLOAT,
                 theta_deg FLOAT,
                 b_deg FLOAT,
                 l_deg FLOAT,
                 lcm_deg FLOAT,
                 A_deg2 FLOAT,
                 A_MSH FLOAT,
                 A_km2 FLOAT,
                 P_Total FLOAT,
                 P_Mean FLOAT,
                 P_Min FLOAT,
                 P_Max FLOAT,
                 P_Std FLOAT,
                 p_key VARCHAR(27),
                 PRIMARY KEY(p_key)
                 );''')

    return 0


def sunspot_continuum_table(row):

    # Define working directory
    cwd = os.getcwd()
    path = os.path.abspath(os.path.join(cwd, os.pardir)) + '/SheffieldSolarCatalog/database/sql/'

    # Connect to the local databas/
    c = s3.connect(path + 'ssc_sql.db')

    # Create the primary key for the feature
    row.append(create_primary_key(row))

    # Create the table if it does not exist
    if str(row[2]) is 'continuum':
        create_sunspot_continuum_table(c)

        # Create a new row if it does not exist
        try:
            c.execute("INSERT INTO continuum_sunspot VALUES" +
                      "(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", row)

        except:
            pass

    if str(row[2]) is 'magnetogram':
        create_sunspot_magnetogram_table(c)

        # Create a new row if it does not exist
        try:
            c.execute("INSERT INTO magnetogram_sunspot VALUES" +
                      "(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", row)

        except:
            pass

    # Save (commit) the changes
    c.commit()

    # Close the connection
    c.close()

    return 0
