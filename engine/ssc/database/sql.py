import sqlite3 as s3
import os


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
    key = key + str(row[4] - 10000) + '-'

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
    path = os.path.abspath(os.path.join(cwd, os.pardir)) + '/database/sql/'

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
            print 'Continuum: UNIQUE constraint failed'

    if str(row[2]) is 'magnetogram':
        create_sunspot_magnetogram_table(c)

        # Create a new row if it does not exist
        try:
            c.execute("INSERT INTO magnetogram_sunspot VALUES" +
                      "(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", row)

        except:
            print 'Magnetogram UNIQUE constraint failed'

    # Save (commit) the changes
    c.commit()

    # Close the connection
    c.close()

    return 0
