'''----------------------------------------------------------------------------

flask.py



----------------------------------------------------------------------------'''


from flask import Flask, render_template, request, g, send_from_directory, session, make_response
from gevent.pywsgi import WSGIServer
from .python.extrapolation import *
from flask import redirect, url_for
from bokeh.resources import INLINE
from .python.live_plot import *
from .python.utility import *
from gevent import monkey
from pathlib import Path
import sqlite3
import json
import os
import datetime
import sys
import string
import uuid
import re

monkey.patch_all()

DATABASE = ''

# Define global variables --------------------------------------------------'''


class att:

    # consists of two boolean elements; the first one is whether the
    # front-end have accessed to the back-end; another is the number
    # of the columns in the table
    block_status = [0,0]

    # Default sql query command
    sql_cmd = "SELECT * FROM continuum LIMIT 1000"

    # start date, end date, start time, end time
    date_formate = '%Y-%m-%d'
    time_formate = '%H:%M:%S'

    sd, st = '',''
    ed, et = '', ''

    # columns of the table
    columns = 0

    # rows of the table
    rows = 0

    # list of all attributes in the table
    attributes = []

    # sunspot type (umbra or penumbra)
    sunspot_type = 'continuum'

    # attribute that should be used in sort
    order = 'Date_obs'

    # Ascending or Descending Order (ASC|DESC)
    order_asc = 'ASC'

    # list of attributes that should be included in the table
    sql_attr = ''

    # first part of the query
    sql_head = ''

    # one part of the query which is considered as the filter
    sql_values = ' '

    # all the headers in the table
    header_all = []

    # first 6 headers in the table
    header1 = []

    # the 6th to the 16th header in the table
    header2 = []

    # other attributes are used in magnetogram exclude first 16 attributes
    header2_1 = []

    # other attributes wich are used in continuum exclude first 16 attributes
    header2_2 = []

    # minimum values for attributes
    values_min = [0] * 21

    # maximum values for attributes
    values_max = [0] * 21

    # all the error message
    error_message = ''

    # Number of records
    list_length = 0

    # Div position left
    position_left = []

    # Div position right
    position_top = []


class att_plot:

    # Requested plot status
    plot_status = 0

    # Bokeh script for Java script
    js_resources = ''

    # bokeh script for css
    css_resources = ''

    # Div frame list
    div_frame_list = []

    # Number of plots
    plot_times = 0

    # Bokeh script
    bokeh_script_list = []

    # Index
    bokeh_index_list = []

    # Plot div from Bokeh
    div_minimize_block_list = []


class att_visual:

    visual_div_full = ''

    visual_script_full = ''

    visual_div = ''

    visual_script = ''

    js_resources = ''

    att_plot.css_resources = ''


class att_visual_full:

    visual_div_full = ''

    visual_script_full = ''

    js_resources = ''

    css_resources = ''

    rows = 0

    columns = 0

    header_t = []

class att_visual_ar:

    visual_div_ar = ''

    visual_script_ar = ''

    js_resources = ''

    css_resources = ''

    range_max = 30

    # Number of equally spaced grid points in the z direction
    Nz = 30

    # Sets the z-scale (1.0 = same scale as the x,y axes)
    zscale = 1

    # Z layer for visualisation
    level = 0

    level_in_mm = 0

    ex_cube = 0

    date = ''

    Instrument = ''

    NOAA = ''

    stream_plot = ''

    path = ''

    fname = ''

class param:

    path_AR = ''

    path_full = ''

    row = []

class download:

    table = []

    header = []

# Define global variables --------------------------------------------------'''


app = Flask(__name__)
app.secret_key = os.urandom(16)

# Add the defined classes to the global namespace
app.add_template_global(att, 'att')
app.add_template_global(att_plot, 'att_plot')
app.add_template_global(att_visual, 'att_visual')
app.add_template_global(att_visual_ar, 'att_visual_ar')
app.add_template_global(att_visual_full, 'att_visual_full')


@app.before_request
def before_request():

    # Connect to the SQL database by the engine
    g.db = sqlite3.connect(DATABASE)


@app.teardown_request
def teardown_request(exception):

    # Break the connection
    if hasattr(g, 'db'):
        g.db.close()


@app.route('/')
def index():

    # The index page is static but handled by Flask
    return render_template('index.html')

@app.route('/extrapolation.html', methods=['GET', 'POST'])
def extrapolation():

    if not ('Nz' in session):
        session['Nz'] = 30
        session['zscale'] = 1
        session['level'] = 0

    if not ('path_AR' in session) or session['path_AR'] == "":
        return redirect("/workstation.html")

    # Make sure that the magnetogram observation is selected
    path_AR = session['path_AR'].replace('continuum', 'magnetogram')

    # Open the fits file, AR
    hdulist = fits.open(path_AR)


    # Fix the broken fits
    hdulist.verify('fix')

    # Save the data
    obs = hdulist[0].data
    header = hdulist[0].header

    # Close the fits files
    hdulist.close()

    # NOAA number of the observation
    session['NOAA'] = header['NOAA']

    # Instrument and type
    session['Instrument'] = header['TELESCOP'] + ' - ' + header['CONTENT']

    # Date of observation
    session['date'] = header['DATE']

    # Setup few variables
    extrapolate = True
    downloading = False

    # Check the request method
    if request.method == 'POST':

        try:

            if (session['Nz'] == int(request.form['Nz']) and
               session['zscale'] == int(request.form['zscale'])):
                extrapolate = False

            if request.form['submit_button'] == 'Download Data':
                downloading = True

            # Number of equally spaced grid points in the z direction
            session['Nz'] = int(request.form['Nz'])

            # Sets the z-scale (1.0 = same scale as the x,y axes)
            session['zscale'] = int(request.form['zscale'])

            # Z layer for visualisation
            session['level'] = int(request.form['slider'])

            # Z layer for visualisation in Mm
            session['level_in_mm'] = format(session['level'] * 0.35, '.4f')

        except Exception:
            pass

    # Magnetic Field Extrapolation
    if extrapolate is True:
        ex_cube = PFFF(obs, nz=session['Nz'],
                                     zscale=session['zscale'])

    if downloading is True:
        if extrapolate is False:
            ex_cube = PFFF(obs, nz=session['Nz'],
                                     zscale=session['zscale'])
        hdf5_path, hdf5_fname = generate_hdf5(ex_cube,
                                              session['NOAA'],
                                              session['date'])

        session['path'] = hdf5_path
        session['fname'] = hdf5_fname

        return send_from_directory(directory=hdf5_path,
                                       filename=hdf5_fname, as_attachment=True)

    # Range Bar maximum value for the HTML
    session['range_max'] = int(session['Nz'] - 1)

    # Visualise the active region
    script, div = Extrapolation_visual(ex_cube['Bz'][session['level']])

    # Save the Bokeh scripts
    visual_div_ar = div
    visual_script_ar = script

    # Store the css amd JavaSrcipt resources
    att_visual_ar.js_resources = INLINE.render_js()
    att_visual_ar.css_resources = INLINE.render_css()

    return render_template('extrapolation.html',
                           visual_div_ar = visual_div_ar,
                           visual_script_ar = visual_script_ar)


@app.route('/full_disk.html', methods=['GET', 'POST'])
def full_disk():

    if not ('path_full' in session) or session['path_full'] == "":
        return redirect("/workstation.html")

    # Full disk visualisation in full screen
    script, div, header = Create_live_fulldisk(session['path_full'],
                                               session['row'], True)

    # Save the Bokeh scripts
    visual_div_full = div
    visual_script_full = script

    # Store the css amd JavaSrcipt resources
    att_visual_full.js_resources = INLINE.render_js()
    att_visual_full.css_resources = INLINE.render_css()

    # Additional info for displaying the fits header
    header_t = header
    rows = len(header)
    columns = len(header[0])

    return render_template('full_disk.html',
                           visual_div_full = visual_div_full,
                           visual_script_full = visual_script_full,
                           header_t = header_t,
                           rows = rows,
                           columns = columns)


@app.route('/download.html', methods=['GET', 'POST'])
def download_data():

    # Reset error message
    session['error_message'] = ""

    # Delete TMP files older than 1 day
    os.system('find ' + str(os.getcwd()) + '/web/static/database/tmp/ -type f -mtime +1 -exec rm {} \;')

    # Clear sql_table
    sql_table = []

    # Send the query to sqlite
    try:

        # Execute the query
        sql_table = g.db.execute(session['sql_cmd'])

    except Exception as e:

        # Error if sending failed
        session['error_message'] = session['error_message'] + \
            "<p> - Error occured when retrieving data.<br></p><br>"

        # Default sql command if something is wrong
        session['sql_cmd'] = "SELECT * FROM continuum LIMIT 1000"

        # Execute the query
        sql_table = g.db.execute(session['sql_cmd'])

    # Create the sql table
    table, header = Create_table(sql_table)

    try:
        # Save the lenght of the table
        session['columns'] = len(table[0])

        # Read the lenght of the table
        session['rows'] = len(table)

    except Exception as e:

        # Error if the table is empyt
        session['error_message'] = session['error_message'] + \
            "<p> - No Data for selected time period. <br></p><br>"

        # Default sql command
        session['sql_cmd'] = "SELECT * FROM continuum LIMIT 1000"

        # Execute the command
        sql_table = g.db.execute(session['sql_cmd'])

        # Create the data table
        table, header = Create_table(sql_table)

        # Read the lenght of the table
        session['columns'] = len(table[0])

        # Read the lenght of the table
        session['rows'] = len(table)

    if session['sql_cmd'] != "SELECT * FROM continuum LIMIT 1000":
        full_sql_table = g.db.execute("SELECT * FROM continuum LIMIT 1000")
        full_table, full_header = Create_table(full_sql_table)

    table = np.array(table)
    table[table == None] = -9999
    dates = [row[0] + ' ' + row[1] for row in table]
    set_date = np.unique(dates)

    # Find all the unique NOAA identifiers in the requested data
    NOAA_already_seen = []
    rows = []
    for x in table:
        if not (x[4] in NOAA_already_seen):
            NOAA_already_seen.append(x[4])
            rows.append(x)

    # Get the image paths for all the AR's and full disks over the time period
    full_disk_paths = {}
    png_AR_paths = {}
    pdf_AR_paths = {}

    for AR in rows:
        # Get AR path to pdf
        path_AR, path_full = pdf_image_path(AR, os.getcwd())
        time = str(AR[0]) + "" + str(AR[1])

        if time in pdf_AR_paths:
            pdf_AR_paths[time].append(path_AR)
        else:
            pdf_AR_paths[time] = [path_AR]

        # Get AR path to png
        path_AR, path_full = png_image_path(AR, os.getcwd())
        if time in png_AR_paths:
            png_AR_paths[time].append(path_AR)
        else:
            png_AR_paths[time] = [path_AR]

        # Get full disk if it doesn't yet exist
        if not (time in full_disk_paths):
            full_disk_paths[time] = path_full
            


    # Download the data from the query
    if request.method == 'POST':

        #Create unique filename for the request
        uid = str(uuid.uuid4())[:8]

        fname = 'SSC_' + uid

        if request.form['download_option'] == 'SQL':

            # Download the full SQL database
            return send_from_directory(directory=str(os.getcwd()) + '/web/static/database/sql/',
                                       filename='ssc_sql.db', as_attachment=True)

        elif request.form['download_option'] == 'HDF5': 

            import pandas as pd

            #df = pd.DataFrame(data=download.table, columns=download.header)

            test = table[:,0]

            df = pd.DataFrame(test)

            df.to_hdf(str(os.getcwd()) + '/web/static/database/tmp/' + fname + '.h5', key='SSC', mode='w')

            # Send the data to the user
            return send_from_directory(directory=str(os.getcwd()) + '/web/static/database/tmp/',
                                       filename=fname + '.h5', as_attachment=True)
            
        elif request.form['download_option'] == 'TXT':
            print(tuple(header))
            # Define the string format
            form = '%10s %10s %10s %10s %7s %4s %8s %8s %8s %9s %8s %8s %8s %7s %7s %14s %14s %14s %14s %14s %14s'

            # Save the requested data
            np.savetxt(str(os.getcwd()) + '/web/static/database/tmp/' + fname + '.txt',
                       np.array(full_table),
                       header=form % tuple(full_header),
                       comments='',
                       delimiter = ' ',
                       fmt = form)

            # Send the data to the user
            return send_from_directory(directory=str(os.getcwd()) + '/web/static/database/tmp/',
                                       filename=fname + '.txt', as_attachment=True)

        elif request.form['download_option'] == 'CSV': 

            # Save the requested data
            np.savetxt(str(os.getcwd()) + '/web/static/database/tmp/' + fname + '.csv',
                       np.array(table),
                       header=str(header),
                       delimiter = ',',
                       fmt = '%s')

            # Send the data to the user
            return send_from_directory(directory=str(os.getcwd()) + '/web/static/database/tmp/',
                                       filename=fname + '.csv', as_attachment=True)


        elif request.form['download_option'] == 'Submit':

            # Send the data to the user
            full_disk_date = request.form['full_disk_date']

            # Convert the date and time to filenames
            date = ''.join(full_disk_date.split()[0].split('-'))
            time = ''.join(full_disk_date.split()[1].split(':'))
            date_time = date + '_' + time

            # Build the path and file name
            dir_path =  str(os.getcwd()) + '/web/static/database/img/AR' + full_disk_date.split()[0] + '/png/'
            fname = [dir_path + 'hmi.ssc.full_disk.continuum.' + date_time + '.png',
                     dir_path + 'hmi.ssc.full_disk.magnetogram.' + date_time + '.png']


            return render_template('download.html', set_date = set_date, fname = fname, png_AR_paths = png_AR_paths, pdf_AR_paths = pdf_AR_paths, full_disk_paths = full_disk_paths)

        # User selects full disk or AR image
        else:
            # Get the image name
            image_name =  (re.findall("[^/]+$",request.form['download_option']))
            # Get the image directory path
            directory = re.findall(".*\/",request.form['download_option'])
            return send_from_directory(directory=os.getcwd() + '/web' +directory[0],filename = image_name[0], as_attachment=True)

    return render_template('download.html', set_date = set_date, fname = '', png_AR_paths = png_AR_paths, pdf_AR_paths = pdf_AR_paths, full_disk_paths = full_disk_paths)


@app.route('/workstation.html', methods=['GET', 'POST'])
def query():

    #Create all the session items needed for the code to run if they do not already exist
    if not ("sunspot_type" in session):
        session['block_status'] = [0,0]
        session['sql_cmd'] = "SELECT * FROM continuum LIMIT 1000"
        session['date_formate'] = '%Y-%m-%d'
        session['time_formate'] = '%H:%M:%S'
        session['columns'] = 0
        session['rows'] = 0
        session['attributes'] = []
        session['sunspot_type'] = 'continuum'
        session['order'] = 'Date_obs'
        session['order_asc'] = 'ASC'
        session['sql_attr'] = ''
        session['sql_head'] = ''
        session['sql_values'] = ' '
        session['header_all'] = []
        session['header1'] = []
        session['header2'] = []
        session['header2_1'] = []
        session['header2_2'] = []
        session['values_min'] = [0]*21
        session['values_max'] = [0]*21
        session['error_message'] = ''
        session['list_length'] = 0
        session['position_left'] = []
        session['position_top'] = []
        session['plots'] = []
    # Default commands
    c1 = "SELECT * FROM continuum"
    c2 = "SELECT * FROM magnetogram"

    # css command
    statistic_height = 0

    # Check the request method
    if request.method == 'POST':
        # clear the error message
        session['error_message'] = ''

        if 'sunspot_type' in request.form:
            #Reset the row number to not cause errors
            session['ARID'] = 0

            # Define the investigated period
            session['sd'] = request.form['start_date']
            session['ed'] = request.form['end_date']
            session['st'] = request.form['start_time']
            session['et'] = request.form['end_time']

            # Get the attributes from the form
            session['attributes'] = request.values.getlist('attributes')

            # set sql head
            if len(session['attributes']) == 0:
                session['sql_attr'] = '*'

            # Read the sql attributes
            else:
                session['sql_attr'] = 'Date_obs,Time_obs,Obs_type,Fea_type,NOAA,'
                for a in range(len(session['attributes'])):
                    session['sql_attr'] = session['sql_attr'] + session['attributes'][a] + ','
                session['sql_attr'] = session['sql_attr'] + 'p_key'

            # Minimum and maximum values for filtering the data
            session['values_min'] = request.values.getlist('values_min')
            session['values_max'] = request.values.getlist('values_max')

            # Define block status
            session['block_status'] = [1, len(session['attributes'])]

            # Sort by both Date_obs and Time_obs
            session['order'] = request.form['order_by']
            session['order_asc'] = request.form['order_asc']

            if session['order'] == 'Time_obs' or session['order'] == 'Date_obs':
               session['order'] = 'Date_obs, Time_obs'

            # Read the sunspot type, umbra or penumbra
            session['sunspot_type'] = request.form['sunspot_type']

            session['sql_values'] = ' '
 
            # set the range of attributes in the query
            for number in range(5, len(session['header_all']) - 1):
                min_value = session['values_min'][number - 5]
                max_value = session['values_max'][number - 5]
                if min_value == '':
                    min_value = '0'
                if max_value == '':
                    max_value = '0'

                # Convert strings to floats if possible
                try:
                    float(min_value) + float(max_value)
                except Exception as e:

                    # Send the error message to the user
                    session['error_message'] = session['error_message'] + "<p> -- " + \
                        "Wrong input when setting attributes.(" + \
                        session['header_all'][number] + ">> minimum:  " + \
                        min_value + ", maximum:  " + max_value + ")</p><br>"
                    continue

                # If no error send the query to the sql server
                if int(min_value) != 0 or int(max_value) != 0:
                    if int(min_value) < int(max_value):

                        # sql command for filtering the values
                        session['sql_values'] = session['sql_values'] + \
                            session['header_all'][number] + " >= " + min_value + \
                            " AND " + session['header_all'][number] + " <= " + \
                            max_value + " AND "

                    # attribute error
                    elif int(min_value) > int(max_value):
                        error_message = error_message + \
                            "<p> -- Wrong input when setting attributes. (" + \
                            header_all[number] + ">> minimum: " + min_value + \
                            ", maximum:  " + max_value + ")</p><br>"

            # Close the filter command
            session['sql_values'] = session['sql_values'] + "END"
            if session['sql_values'] == " END":
                session['sql_values'] = session['sql_values'].replace(" END", "")

            # Close and continue the filter command
            else:
                session['sql_values'] = session['sql_values'].replace("AND END", "")

            # No filter option
            if session['sql_values'] != '':
                session['sql_values'] = " AND " + session['sql_values']

            # Construct the sql command
            session['sql_head'] = 'SELECT ' + session['sql_attr'] + ' FROM '

            # sql command, if no time interval selected
            if session['sd'] == session['ed'] and session['st'] == session['et']:
               session['sql_cmd'] = session['sql_head'] + session['sunspot_type'] + \
                             " WHERE (Date_obs = '" + session['sd'] + "' AND Time_obs = '" + session['st'] + "')" + \
                             session['sql_values'] + ' ORDER BY ' + session['order'] + ' ' + session['order_asc'] + " LIMIT 1000"

            # in case of diffrent times on the same date
            elif session['sd'] == session['ed']:
               session['sql_cmd'] = session['sql_head'] + session['sunspot_type'] + \
                             " WHERE (Date_obs = '" + session['sd'] + "' AND Time_obs >= '" + session['st'] + "' AND Time_obs <= '" + session['et'] + "')" + \
                             session['sql_values'] + ' ORDER BY ' + session['order'] + ' ' + session['order_asc'] + " LIMIT 1000"

            # in case of difffrent dates
            else:
               session['sql_cmd'] = session['sql_head'] + session['sunspot_type'] + \
                             " WHERE ((Date_obs = '" + session['sd'] + "' AND Time_obs >= '" + session['st'] + "')" + \
                             " OR (Date_obs > '" + session['sd'] + "' AND Date_obs < '" + session['ed'] + "')" + \
                             " OR (Date_obs = '"    + session['ed'] + "' AND Time_obs <= '" + session['et'] + "'))" + \
                             session['sql_values'] + ' ORDER BY ' + session['order'] + ' ' + session['order_asc'] + " LIMIT 1000"


        #If the user has tried to add a plot add the information to create it to the plots list in
        #sessions

        if keyword_check(request.form, 'plot_type') is True:
            # plot attributes for line plot
            xl = request.form['xl']
            yl = request.form['yl']
            line_col = request.form['line_col']

            # plot attributes for scatter plot
            x = request.form['x']
            y = request.form['y']
            s = request.form['s']
            c = request.form['c']

            # plot attributes for histogram plot
            v = request.form['v']
            density = request.form['histogram_den']
            fit = request.form['histogram_fit']
            color = request.form['histogram_col']
            bin_n = request.form['histogram_bin']

            # plot attributes for bivariate histogram plot
            biv_v = request.form['biv_v']
            biv_w = request.form['biv_w']
            biv_w_bin = request.form['biv_w_bin']

            #Save the information to create a line plot if that is what the user tried to add
            if request.form['plot_type'] == 'line':
                session['plots'].append({"plot_type": "Line Plot",
                                         "xl": xl,
                                         "yl": yl,
                                         "line_col":line_col})

            #Save the information to create a scatter plot if that is what the user tried to add
            elif request.form['plot_type'] == 'scatter_2d':
                session['plots'].append({"plot_type": "Scatter Plot",
                                         "x": x,
                                         "y": y,
                                         "s": s,
                                         "c": c})

            #Save the information to create a histogram if that is what the user tried to add
            elif request.form['plot_type'] == 'histogram': 
                session['plots'].append({"plot_type": "Histogram Plot",
                                         "v": v,
                                         "density": density,
                                         "fit": fit,
                                         "color": color,
                                         "bin_n": bin_n})

            #Save the information to create a Bivariate Histogram if that is what the user tried to add
            elif request.form['plot_type'] == 'biv_hist':
                session['plots'].append({"plot_type": "Bivariate Histogram",
                                         "biv_v": biv_v,
                                         "biv_w": biv_w,
                                         "biv_w_bin": biv_w_bin})

        if keyword_check(request.form, 'AR_ID') is True:
            # The index of the selected row
            selected_row = int(request.form['AR_ID'])
            session['ARID'] = selected_row

        #Redirect the user back to this page to stop them creating more graphs on refresh
        return redirect("/workstation.html")

    # Get the whole header in the complete table dpeending on sunspot type
    if session['sunspot_type'] == "magnetogram":
        full_sql_table = g.db.execute(c2)
    else:
        full_sql_table = g.db.execute(c1)

    table_all, header_all_1 = Create_table(full_sql_table)

    # Save the header
    session['header_all'] = header_all_1

    # Select the last observation if none saved from old requests
    if not ("sd" in session):
        session['sd'], session['st'] = table_all[-1][0], table_all[-1][1]
        session['ed'], session['et'] = session['sd'], session['st']

    # Initial SQL command, displaying only the last observation if none saved from old requests
    if not ("sql_cmd" in session):
        session['sql_cmd'] = "SELECT * FROM continuum " + \
                  "WHERE Date_obs = '" + session['sd'] + "' AND Time_obs = '" + session['st'] + "' LIMIT 1000" 


    # Clear sql_table
    sql_table = []

    # Send the query to sqlite
    try:

        # Execute the query
        sql_table = g.db.execute(session['sql_cmd'])

        #Get primary keys if id not in attributes
        if not ("id" in session['attributes']) and not len(session['attributes']) == 0:
            #Get primary keys
            p_keys = g.db.execute(session['sql_cmd'])
            temp_row = Get_primary_key(p_keys)
            if session['sunspot_type'] == "magnetogram":
                unedited_full_sql_table = g.db.execute(c2)
            else:
                unedited_full_sql_table = g.db.execute(c1)
            actual_row = Get_primary_key(unedited_full_sql_table)
    except Exception as e:

        # Error if sending failed
        session['error_message'] = session['error_message'] + \
            "<p> - Error occured when retrieving data.<br></p><br>"

        # Default sql command if something is wrong
        session['sql_cmd'] = "SELECT * FROM continuum"

        # Execute the query
        sql_table = g.db.execute(session['sql_cmd'])

    # Create the sql table
    table, header = Create_table(sql_table)

    try:
        # Save the lenght of the table
        session['columns'] = len(table[0])

        # Read the lenght of the table
        session['rows'] = len(table)

    except Exception as e:

        # Error if the table is empyt
        session['error_message'] = session['error_message'] + \
            "<p> - No Data for selected time period. <br></p><br>"

        # Default sql command
        session['sql_cmd'] = "SELECT * FROM continuum LIMIT 1000"

        # Execute the command
        sql_table = g.db.execute(session['sql_cmd'])

        # Create the data table
        table, header = Create_table(sql_table)

        # Read the lenght of the table
        session['columns'] = len(table[0])

        # Read the lenght of the table
        session['rows'] = len(table)

    # Create data for downloading
    data = []
    data = data + header

    # Download
    for row in table:
        new_row = [] + row
        new_row[0] = '\r\n' + str(row[0])
        data = data + new_row

    # Dump the data
    data = json.dumps(data)

    try:

        # Set up the diemnsions of the obtained data table
        statistic_height = len(table) * 26 + 43

    except Exception as e:

        # Set to zero if table is empyt
        statistic_height = 0

    # Obtain the basic info (number of elements etc...) of the table
    info = Query_info(table)

    # Create the AR and Full disk plots
    if ('ARID' in session):
        selected_row = session['ARID']
    else:
        session['ARID'] = 0
        selected_row = 0

    # Define the selected row
    table_live =table_all
    # Execute the query
    if table == table_all:
        row = table_all[selected_row]

    # Find row depending by matching first six rows
    elif ("id" in session['attributes']):
        temp_row = table[selected_row]
        row = next(row for row in table_all if row[0] == temp_row[0] and \
                                               row[1] == temp_row[1] and \
                                               row[2] == temp_row[2] and \
                                               row[3] == temp_row[3] and \
                                               row[4] == temp_row[4] and \
                                               row[5] == temp_row[5])
    # Find row depending on primary key
    else:
        temp_row = temp_row[selected_row]
        row = table_all[actual_row.index(temp_row)]

    session['row'] = row

    # Define the filename of the associated image
    session['path_AR'], session['path_full'] = html_image_path(row, os.getcwd())

    # NOAA = str(table[int(request.form['AR_ID'])][4])
    script_html, div_html = Create_live_AR(session['path_AR'],
                                           session['path_full'], table_live, row)


    script_html_full, div_html_full = Create_live_fulldisk(session['path_full'],
                                                           row, False)

    att_visual.visual_div_full = div_html_full
    att_visual.visual_script_full = script_html_full

    att_visual.visual_div = div_html
    att_visual.visual_script = script_html

    att_visual.js_resources = INLINE.render_js()
    att_visual.css_resources = INLINE.render_css()

    #remove plots the user closed
    if 'deleted_plots' in request.cookies:
        #Get the plots to remove and sperate them into a list
        deleted_plots = (request.cookies.get('deleted_plots')).split(',')
        deleted_plots.remove('')
        #Order the plots so that they are removed in descending order so as not to interfere with
        #the rest of the deletions
        deleted_plots = list(map(int, deleted_plots))
        deleted_plots.sort(reverse = True)
        #Remove deleted plots
        for plot in deleted_plots:
            if len(session['plots']) >= plot:
                del session['plots'][plot-1]
    
    #Create variables needed to display the plots
    js_resources = ''
    css_resources = ''
    plot_times = 0
    div_frame_list = []
    div_minimize_block_list = []
    bokeh_script_list = []
    bokeh_index_list = []

    #Variables to keep track of errors
    plots_index = 0
    error_list = []

    # Display the plot(s)
    for plot in session['plots']:
        plot_status = 0
        global script, div
        # Define some local variables
        script = ''
        active_bokeh = []

        # Line plot
        if plot['plot_type'] == 'Line Plot':

            # operation_that_can_throw_ioerror
            try:

                # Create the actual plot and save the Bokeh script
                script, div = Create_live_2D_line_plot(table, header,
                                                       plot['xl'], plot['yl'], plot['line_col'])

            # Error if no data, handle_the_exception_somehow
            except Exception as e:
                session['error_message'] = session['error_message'] + \
                    "<p> -- Creating line plot failed.</p><br> <p>" + \
                    str(e) + "</p><br>"
                error_list.append(plots_index)

            # Set few varaibles, if try is not failed
            # another_operation_that_can_throw_ioerror
            else:
                plot_status = 1
                plot_times = plot_times + 1

            # Render the script for the front end
            # something_we_always_need_to_do
            finally:
                js_resources = INLINE.render_js()
                css_resources = INLINE.render_css()

        # 2-d scatter plot
        elif plot['plot_type'] == "Scatter Plot":

            try:

                # Create the actual plot and save the Bokeh script
                script, div = Create_live_2D_scatter_plot(table, header,
                                                          plot['x'], plot['y'], plot['c'], plot['s'])

            # Error if no data
            except Exception as e:
                session['error_message'] = session['error_message'] + \
                    "<p> -- Creating scatter plot failed.</p><br> <p>" + \
                    str(e) + "</p><br>"
                error_list.append(plots_index)

            # Set few varaibles
            else:
                plot_status = 1
                plot_times = plot_times + 1

            # Render the script for the front end
            finally:
                js_resources = INLINE.render_js()
                css_resources = INLINE.render_css()

        # Histogram
        elif plot['plot_type'] == "Histogram Plot":
            try:
                # Create the actual plot and save the Bokeh script
                script, div = Create_live_histogram_plot(table, header, plot['v'],
                                                         plot['density'], plot['fit'], plot['bin_n'],
                                                         plot['color'])

            # Error if no data
            except Exception as e:
                session['error_message'] = session['error_message'] + \
                    "<p> -- Creating histogram plot failed.</p><br> <p>" + \
                    str(e) + "</p><br>"
                error_list.append(plots_index)


            # Set few varaibles
            else:
                plot_status = 1
                plot_times = plot_times + 1

            # Render the script for the front end
            finally:
                js_resources = INLINE.render_js()
                css_resources = INLINE.render_css()

        # Bivariate Histogram
        elif plot['plot_type'] == "Bivariate Histogram":
            try:

                # Create the actual plot and save the Bokeh script
                script, div = Create_live_bivariate_histogram_plot(table,
                                                                   header,
                                                                   plot['biv_v'],
                                                                   plot['biv_w'],
                                                                   plot['biv_w_bin'])

            # Error if no data
            except Exception as e:
                session['error_message'] = session['error_message'] + \
                    "<p> -- Creating bivariate plot failed.</p><br> <p>" + \
                    str(e) + "</p><br>"
                error_list.append(plots_index)

            # Set few varaibles
            else:
                plot_status = 1
                plot_times = plot_times + 1

            # Render the script for the front end
            finally:
                js_resources = INLINE.render_js()
                css_resources = INLINE.render_css()

        # Create the div frame for the plots
        if plot_status == 1:
            # Create div_frame and bokeh_script
            temp = type('object', (object,), {'plot_type' : plot['plot_type'], 'plot_times' : plot_times})
            div_frame, div_minimize_block, bokeh_script = Bokehscript(temp,
                                                                      div,
                                                                      script)

        else:
            div_frame = ''
            div_minimize_block = ''
            bokeh_script = ''



        active_bokeh = request.values.getlist('bokeh')

        # Send the plot scripts to the front end
        if script != '' and div != '' and div_frame != '':
            div_frame_list.append(div_frame)
            div_minimize_block_list.append(div_minimize_block)
            bokeh_script_list.append(bokeh_script)
            bokeh_index_list.append(str(plot_times))
            active_bokeh.append(str(plot_times))

        # New plot windows if there are more than one plot request
        new_div_frame_list = []
        new_div_minimize_block_list = []
        new_bokeh_script_list = []

        # Append new windows
        if active_bokeh != []:
            plot_status = 1
            for index in range(0, len(div_frame_list)):
                for active_index in active_bokeh:
                    if active_index == bokeh_index_list[index - 1]:

                        df = div_frame_list[index - 1]
                        new_div_frame_list.append(df)

                        dv = div_minimize_block_list[index - 1]
                        new_div_minimize_block_list.append(dv)

                        bs = bokeh_script_list[index - 1]
                        new_bokeh_script_list.append(bs)
                        break

        else:
            if len(div_frame_list) != 0:

                df = div_frame_list[len(div_frame_list) - 1]
                new_div_frame_list = new_div_frame_list.append(df)

                dn = div_minimize_block_list[len(div_minimize_block_list) - 1]
                new_div_minimize_block_list = \
                    new_div_minimize_block_list.append(dn)

                pkl = len(bokeh_script_list)
                bs = bokeh_script_list[pkl - 1]
                new_bokeh_script_list = new_bokeh_script_list.append(bs)

        # Position of the plot windows
        session['list_length'] = len(div_frame_list)
        if session['list_length'] != 0:
            session['position_left'] = []
            session['position_top'] = []
            for x in range(0, session['list_length']):

                # Define the corners of the window
                print(x)
                left = x
                top = x * 350
                session['position_left'].append(left)
                session['position_top'].append(top)

        plots_index = plots_index + 1

    for plot in error_list:
        del session['plots'][plot]

    # Replace None's with -99999
    table = np.array(table)
    table[table == None] = -9999 

    # Save the table and header globally for the download function()
    download.table, download.header = table, header

    general_plot_options = [x for x in header if x != "Obs_type" and x != "Fea_type" ]
    hist_plot_options = [x for x in general_plot_options if x != "Date_obs" and x != "Time_obs"]

    # Render the front end
    resp = make_response(render_template('/workstation.html',
                         table=table,
                         data=data,
                         header=header,
                         info=info,
                         statistic_height=statistic_height,
                         js_resources = js_resources,
                         css_resources = css_resources,
                         div_frame_list = div_frame_list,
                         div_minimize_block_list = div_minimize_block_list,
                         bokeh_script_list = bokeh_script_list,
                         general_plot_options = general_plot_options,
                         hist_plot_options = hist_plot_options))
    resp.set_cookie('deleted_plots', '', expires=0)
    return resp



def start(ip, port):

    global DATABASE

    # Connect the database from the engine.
    directory = Path(__file__).parents[2]
    DATABASE = str(directory) + '/SheffieldSolarCatalog/web/static/database/sql/ssc_sql.db'

    # Use gevent WSGI server instead of the Flask
    #http = WSGIServer((ip, port), app.wsgi_app, keyfile=str(directory) + '/certs/server.key', certfile=str(directory) + '/certs/server.crt')
    http = WSGIServer((ip, port), app.wsgi_app)
    
    # Start the server
    http.serve_forever()

    return 0
