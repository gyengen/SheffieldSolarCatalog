'''----------------------------------------------------------------------------

flask.py



----------------------------------------------------------------------------'''


from flask import Flask, render_template, request, g, send_from_directory, session
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

monkey.patch_all()

DATABASE = ''

# Define global variables --------------------------------------------------'''


class att:

    # consists of two boolean elements; the first one is whether the
    # front-end have accessed to the back-end; another is the number
    # of the columns in the table
    block_status = [0,0]

    # Default sql query command
    sql_cmd = "SELECT * FROM continuum"

    # start date, end date, start time, end time
    date_formate = '%Y-%m-%d'
    time_formate = '%H:%M:%S'

    sd, st = '',''
    ed, et = '', ''

    # columns of the table
    columns = 0

    # rows of the table
    rows = 0

    # selected row id
    selected_row = 0

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

    # Make sure that the magnetogram observation is selected
    path_AR = param.path_AR.replace('continuum', 'magnetogram')

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
    att_visual_ar.NOAA = header['NOAA']

    # Instrument and type
    att_visual_ar.Instrument = header['TELESCOP'] + ' - ' + header['CONTENT']

    # Date of observation
    att_visual_ar.date = header['DATE']

    # Setup few variables
    extrapolate = True
    downloading = False

    # Check the request method
    if request.method == 'POST':

        try:

            if (att_visual_ar.Nz == int(request.form['Nz']) and
               att_visual_ar.zscale == int(request.form['zscale'])):
                extrapolate = False

            if request.form['submit_button'] == 'Download Data':
                downloading = True

            # Number of equally spaced grid points in the z direction
            att_visual_ar.Nz = int(request.form['Nz'])

            # Sets the z-scale (1.0 = same scale as the x,y axes)
            att_visual_ar.zscale = int(request.form['zscale'])

            # Z layer for visualisation
            att_visual_ar.level = int(request.form['slider'])

            # Z layer for visualisation in Mm
            att_visual_ar.level_in_mm = format(att_visual_ar.level * 0.35, '.4f')

        except Exception:
            pass

    # Magnetic Field Extrapolation
    if extrapolate is True:
        att_visual_ar.ex_cube = PFFF(obs, nz=att_visual_ar.Nz,
                                     zscale=att_visual_ar.zscale)

    if downloading is True:

        hdf5_path, hdf5_fname = generate_hdf5(att_visual_ar.ex_cube,
                                              att_visual_ar.NOAA,
                                              att_visual_ar.date)

        att_visual_ar.path = hdf5_path
        att_visual_ar.fname = hdf5_fname

        return redirect(url_for('download_extrapolation'))

    # Range Bar maximum value for the HTML
    att_visual_ar.range_max = int(att_visual_ar.Nz - 1)

    # Visualise the active region
    script, div = Extrapolation_visual(att_visual_ar.ex_cube['Bz'][att_visual_ar.level])

    # Save the Bokeh scripts
    att_visual_ar.visual_div_ar = div
    att_visual_ar.visual_script_ar = script

    # Store the css amd JavaSrcipt resources
    att_visual_ar.js_resources = INLINE.render_js()
    att_visual_ar.css_resources = INLINE.render_css()

    return render_template('extrapolation.html')


@app.route('/full_disk.html', methods=['GET', 'POST'])
def full_disk():

    # Full disk visualisation in full screen
    script, div, header = Create_live_fulldisk(param.path_full,
                                               param.row, True)

    # Save the Bokeh scripts
    att_visual_full.visual_div_full = div
    att_visual_full.visual_script_full = script

    # Store the css amd JavaSrcipt resources
    att_visual_full.js_resources = INLINE.render_js()
    att_visual_full.css_resources = INLINE.render_css()

    # Additional info for displaying the fits header
    att_visual_full.header_t = header
    att_visual_full.rows = len(header)
    att_visual_full.columns = len(header[0])

    return render_template('full_disk.html')


@app.route('/download.html', methods=['GET', 'POST'])
def download_data():

    # Delete TMP files older than 1 day
    os.system('find ' + str(os.getcwd()) + '/database/tmp/ -type f -mtime +1 -exec rm {} \;')

    set_date = np.unique(download.table[:,0] + ' ' + download.table[:,1])

    # Download the data from the query
    if request.method == 'POST':

        #Create unique filename for the request
        uid = str(uuid.uuid4())[:8]

        fname = 'SSC_' + uid

        if request.form['download_option'] == 'SQL':

            # Download the full SQL database
            return send_from_directory(directory=str(os.getcwd()) + '/database/sql/',
                                       filename='ssc_sql.db', as_attachment=True)

        if request.form['download_option'] == 'HDF5': 

            import pandas as pd

            #df = pd.DataFrame(data=download.table, columns=download.header)

            test = download.table[:,0]
            print(test)
            df = pd.DataFrame({'A',test})

            df.to_hdf(str(os.getcwd()) + '/database/tmp/' + fname + '.h5', key='SSC', mode='w')

            # Send the data to the user
            return send_from_directory(directory=str(os.getcwd()) + '/database/tmp/',
                                       filename=fname + '.h5', as_attachment=True)
            
        if request.form['download_option'] == 'TXT':
            print(tuple(download.header))
            # Define the string format
            form = '%10s %10s %10s %10s %7s %4s %8s %8s %8s %9s %8s %8s %8s %7s %7s %14s %14s %14s %14s %14s %14s'

            # Save the requested data
            np.savetxt(str(os.getcwd()) + '/database/tmp/' + fname + '.txt',
                       np.array(download.table),
                       header=form % tuple(download.header),
                       comments='',
                       delimiter = ' ',
                       fmt = form)

            # Send the data to the user
            return send_from_directory(directory=str(os.getcwd()) + '/database/tmp/',
                                       filename=fname + '.txt', as_attachment=True)

        if request.form['download_option'] == 'CSV': 

            # Save the requested data
            np.savetxt(str(os.getcwd()) + '/database/tmp/' + fname + '.csv',
                       np.array(download.table),
                       header=str(download.header),
                       delimiter = ',',
                       fmt = '%s')

            # Send the data to the user
            return send_from_directory(directory=str(os.getcwd()) + '/database/tmp/',
                                       filename=fname + '.csv', as_attachment=True)


        if request.form['download_option'] == 'Submit':

            # Send the data to the user
            full_disk_date = request.form['full_disk_date']

            # Convert the date and time to filenames
            date = ''.join(full_disk_date.split()[0].split('-'))
            time = ''.join(full_disk_date.split()[1].split(':'))
            date_time = date + '_' + time

            # Build the path and file name
            dir_path =  str(os.getcwd()) + '/database/img/AR' + full_disk_date.split()[0] + '/png/'
            fname = [dir_path + 'hmi.ssc.full_disk.continuum.' + date_time + '.png',
                     dir_path + 'hmi.ssc.full_disk.magnetogram.' + date_time + '.png']


            return render_template('download.html', set_date = set_date, fname = fname)


    return render_template('download.html', set_date = set_date, fname = '')


@app.route('/workstation.html', methods=['GET', 'POST'])
def query():

    # Default commands
    c1 = "SELECT * FROM continuum"
    c2 = "SELECT * FROM continuum"

    # Get the whole header in the complete table
    table_all, header_all_1 = Create_table(g.db.execute(c1))

    # Save the header
    att.header_all = header_all_1

    # Select the last observation
    att.sd, att.st = table_all[-1][0], table_all[-1][1]
    att.ed, att.et = att.sd, att.st

    # Initial SQL command, displaying only the last observation
    att.sql_cmd = "SELECT * FROM continuum " + \
                  "WHERE Date_obs = '" + att.sd + "' AND Time_obs = '" + att.st + "'" 

    # css command
    statistic_height = 0

    # Check the request method
    if request.method == 'POST':

        # clear the error message
        att.error_message = ''

        if 'sunspot_type' in request.form:

            # Define the investigated period
            att.sd = request.form['start_date']
            att.ed = request.form['end_date']
            att.st = request.form['start_time']
            att.et = request.form['end_time']

            # Get the attributes from the form
            att.attributes = request.values.getlist('attributes')

            # set sql head
            if len(att.attributes) == 0:
                att.sql_attr = '*'

            # Read the sql attributes
            else:
                att.sql_attr = 'Date_obs,Time_obs,Obs_type,Fea_type,NOAA,'
                for a in range(len(att.attributes)):
                    att.sql_attr = att.sql_attr + att.attributes[a] + ','
                att.sql_attr = att.sql_attr + 'p_key'

            # Minimum and maximum values for filtering the data
            att.values_min = request.values.getlist('values_min')
            att.values_max = request.values.getlist('values_max')

            # Define block status
            att.block_status = [1, len(att.attributes)]

            # Sort by both Date_obs and Time_obs
            att.order = request.form['order_by']
            att.order_asc = request.form['order_asc']

            if att.order == 'Time_obs' or att.order == 'Date_obs':
               att.order = 'Date_obs, Time_obs'

            # Read the sunspot type, umbra or penumbra
            att.sunspot_type = request.form['sunspot_type']

            att.sql_values = ' '
 
            # set the range of attributes in the query
            for number in range(5, len(att.header_all) - 1):
                min_value = att.values_min[number - 5]
                max_value = att.values_max[number - 5]
                if min_value == '':
                    min_value = '0'
                if max_value == '':
                    max_value = '0'

                # Convert strings to floats if possible
                try:
                    float(min_value) + float(max_value)
                except Exception as e:

                    # Send the error message to the user
                    att.error_message = att.error_message + "<p> -- " + \
                        "Wrong input when setting attributes.(" + \
                        att.header_all[number] + ">> minimum:  " + \
                        min_value + ", maximum:  " + max_value + ")</p><br>"
                    continue

                # If no error send the query to the sql server
                if int(min_value) != 0 or int(max_value) != 0:
                    if int(min_value) < int(max_value):

                        # sql command for filtering the values
                        att.sql_values = att.sql_values + \
                            att.header_all[number] + " >= " + min_value + \
                            " AND " + att.header_all[number] + " <= " + \
                            max_value + " AND "

                    # attribute error
                    elif int(min_value) > int(max_value):
                        error_message = error_message + \
                            "<p> -- Wrong input when setting attributes. (" + \
                            header_all[number] + ">> minimum: " + min_value + \
                            ", maximum:  " + max_value + ")</p><br>"

            # Close the filter command
            att.sql_values = att.sql_values + "END"
            if att.sql_values == " END":
                att.sql_values = att.sql_values.replace(" END", "")

            # Close and continue the filter command
            else:
                att.sql_values = att.sql_values.replace("AND END", "")

            # No filter option
            if att.sql_values != '':
                att.sql_values = " AND " + att.sql_values

            # Construct the sql command
            att.sql_head = 'SELECT ' + att.sql_attr + ' FROM '

            # sql command, if no time interval selected
            if att.sd == att.ed and att.st == att.et:
               att.sql_cmd = att.sql_head + att.sunspot_type + \
                             " WHERE (Date_obs = '" + att.sd + "' AND Time_obs = '" + att.st + "')" + \
                             att.sql_values + ' ORDER BY ' + att.order + ' ' + att.order_asc

            # in case of diffrent times on the same date
            elif att.sd == att.ed:
               att.sql_cmd = att.sql_head + att.sunspot_type + \
                             " WHERE (Date_obs = '" + att.sd + "' AND Time_obs >= '" + att.st + "' AND Time_obs <= '" + att.et + "')" + \
                             att.sql_values + ' ORDER BY ' + att.order + ' ' + att.order_asc

            # in case difffrent dates
            else:
               att.sql_cmd = att.sql_head + att.sunspot_type + \
                             " WHERE ((Date_obs = '" + att.sd + "' AND Time_obs >= '" + att.st + "')" + \
                             " OR (Date_obs > '" + att.sd + "' AND Date_obs < '" + att.ed + "')" + \
                             " OR (Date_obs = '"    + att.ed + "' AND Time_obs <= '" + att.et + "'))" + \
                             att.sql_values + ' ORDER BY ' + att.order + ' ' + att.order_asc

    # Clear sql_table
    sql_table = []

    # Send the query to sqlite
    try:

        # Execute the query
        sql_table = g.db.execute(att.sql_cmd)

    except Exception as e:

        # Error if sending failed
        att.error_message = att.error_message + \
            "<p> - Error occured when retrieving data.<br></p><br>"

        # Default sql command if something is wrong
        att.sql_cmd = "SELECT * FROM continuum"

        # Execute the query
        sql_table = g.db.execute(att.sql_cmd)

    # Create the sql table
    table, header = Create_table(sql_table)

    try:
        # Save the lenght of the table
        att.columns = len(table[0])

        # Read the lenght of the table
        att.rows = len(table)

    except Exception as e:

        # Error if the table is empyt
        att.error_message = att.error_message + \
            "<p> - No Data for selected time period. <br></p><br>"

        # Default sql command
        att.sql_cmd = "SELECT * FROM continuum"

        # Execute the command
        sql_table = g.db.execute(att.sql_cmd)

        # Create the data table
        table, header = Create_table(sql_table)

        # Read the lenght of the table
        att.columns = len(table[0])

        # Read the lenght of the table
        att.rows = len(table)

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
    if keyword_check(request.form, 'AR_ID') is True:
        print ("dwdw")
        print ()
        # The index of the selected row
        att.selected_row = int(request.form['AR_ID'])
        session['ARID'] = att.selected_row
    elif ('ARID' in session):
        att.selected_row = session['ARID']
    # Define the selected row
    if att.sunspot_type == 'magnetogram':
        # Execute the query
        param.row = table_all[att.selected_row]
        table_live =table_all

    else:
        # Execute the query
        param.row = table_all[att.selected_row]
        table_live = table_all


    # Define the filename of the associated image
    param.path_AR, param.path_full = html_image_path(param.row, os.getcwd())

    # NOAA = str(table[int(request.form['AR_ID'])][4])
    script_html, div_html = Create_live_AR(param.path_AR,
                                           param.path_full, table_live, param.row)


    script_html_full, div_html_full = Create_live_fulldisk(param.path_full,
                                                           param.row, False)

    att_visual.visual_div_full = div_html_full
    att_visual.visual_script_full = script_html_full

    att_visual.visual_div = div_html
    att_visual.visual_script = script_html

    att_visual.js_resources = INLINE.render_js()
    att_visual.css_resources = INLINE.render_css()


    # Display the plot(s)
    if keyword_check(request.form, 'plot_type') is True:

        global script, div
        # Define some local variables
        script = ''
        active_bokeh = []

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

        # Line plot
        if request.form['plot_type'] == 'line':

            # operation_that_can_throw_ioerror
            try:

                # Create the actual plot and save the Bokeh script
                script, div = Create_live_2D_line_plot(table, header,
                                                       xl, yl, line_col)

            # Error if no data, handle_the_exception_somehow
            except Exception as e:
                att.error_message = att.error_message + \
                    "<p> -- Creating line plot failed.</p><br> <p>" + \
                    str(e) + "</p><br>"

            # Set few varaibles, if try is not failed
            # another_operation_that_can_throw_ioerror
            else:
                att_plot.plot_status = 1
                att_plot.plot_type = "Line Plot"
                att_plot.plot_times = att_plot.plot_times + 1

            # Render the script for the front end
            # something_we_always_need_to_do
            finally:
                att_plot.js_resources = INLINE.render_js()
                att_plot.css_resources = INLINE.render_css()

        # 2-d scatter plot
        elif request.form['plot_type'] == 'scatter_2d':

            try:

                # Create the actual plot and save the Bokeh script
                script, div = Create_live_2D_scatter_plot(table, header,
                                                          x, y, c, s)

            # Error if no data
            except Exception as e:
                att.error_message = att.error_message + \
                    "<p> -- Creating scatter plot failed.</p><br> <p>" + \
                    str(e) + "</p><br>"

            # Set few varaibles
            else:
                att_plot.plot_status = 1
                att_plot.plot_type = "Scatter Plot"
                att_plot.plot_times = att_plot.plot_times + 1

            # Render the script for the front end
            finally:
                att_plot.js_resources = INLINE.render_js()
                att_plot.css_resources = INLINE.render_css()

        # Histogram
        elif request.form['plot_type'] == 'histogram':
            try:
                # Create the actual plot and save the Bokeh script
                script, div = Create_live_histogram_plot(table, header, v,
                                                         density, fit, bin_n,
                                                         color)

            # Error if no data
            except Exception as e:
                att.error_message = att.error_message + \
                    "<p> -- Creating histogram plot failed.</p><br> <p>" + \
                    str(e) + "</p><br>"

            # Set few varaibles
            else:
                att_plot.plot_status = 1
                att_plot.plot_type = "Histogram Plot"
                att_plot.plot_times = att_plot.plot_times + 1

            # Render the script for the front end
            finally:
                att_plot.js_resources = INLINE.render_js()
                att_plot.css_resources = INLINE.render_css()

        # Bivariate Histogram
        elif request.form['plot_type'] == 'biv_hist':
            try:

                # Create the actual plot and save the Bokeh script
                script, div = Create_live_bivariate_histogram_plot(table,
                                                                   header,
                                                                   biv_v,
                                                                   biv_w,
                                                                   biv_w_bin)

            # Error if no data
            except Exception as e:
                att.error_message = att.error_message + \
                    "<p> -- Creating bivariate plot failed.</p><br> <p>" + \
                    str(e) + "</p><br>"

            # Set few varaibles
            else:
                att_plot.plot_status = 1
                att_plot.plot_type = "Bivariate Histogram"
                att_plot.plot_times = att_plot.plot_times + 1

            # Render the script for the front end
            finally:
                att_plot.js_resources = INLINE.render_js()
                att_plot.css_resources = INLINE.render_css()

        # Create the div frame for the plots
        if att_plot.plot_status == 1:
            # Create div_frame and bokeh_script
            div_frame, div_minimize_block, bokeh_script = Bokehscript(att_plot,
                                                                      div,
                                                                      script)

        else:
            div_frame = ''
            div_minimize_block = ''
            bokeh_script = ''

        active_bokeh = request.values.getlist('bokeh')

        # Send the plot scripts to the front end
        if script != '' and div != '' and div_frame != '':
            att_plot.div_frame_list.append(div_frame)
            att_plot.div_minimize_block_list.append(div_minimize_block)
            att_plot.bokeh_script_list.append(bokeh_script)
            att_plot.bokeh_index_list.append(str(att_plot.plot_times))
            active_bokeh.append(str(att_plot.plot_times))

        # New plot windows if there are more than one plot request
        new_div_frame_list = []
        new_div_minimize_block_list = []
        new_bokeh_script_list = []

        # Append new windows
        if active_bokeh != []:
            att_plot.plot_status = 1
            for index in range(0, len(att_plot.div_frame_list)):
                for active_index in active_bokeh:
                    if active_index == att_plot.bokeh_index_list[index - 1]:

                        df = att_plot.div_frame_list[index - 1]
                        new_div_frame_list.append(df)

                        dv = att_plot.div_minimize_block_list[index - 1]
                        new_div_minimize_block_list.append(dv)

                        bs = att_plot.bokeh_script_list[index - 1]
                        new_bokeh_script_list.append(bs)
                        break

        else:
            if len(att_plot.div_frame_list) != 0:

                df = att_plot.div_frame_list[len(att_plot.div_frame_list) - 1]
                new_div_frame_list = new_div_frame_list.append(df)

                dn = div_minimize_block_list[len(div_minimize_block_list) - 1]
                new_div_minimize_block_list = \
                    new_div_minimize_block_list.append(dn)

                pkl = len(att_plot.bokeh_script_list)
                bs = att_plot.bokeh_script_list[pkl - 1]
                new_bokeh_script_list = new_bokeh_script_list.append(bs)

        # Position of the plot windows
        att.list_length = len(att_plot.div_frame_list)
        if att.list_length != 0:
            att.position_left = []
            att.position_top = []
            for x in range(0, att.list_length):

                # Define the corners of the window
                print(x)
                left = x
                top = x * 350
                att.position_left.append(left)
                att.position_top.append(top)

    # Replace None's with -99999
    table = np.array(table)
    table[table == None] = -9999 

    # Save the table and header globally for the download function()
    download.table, download.header = table, header

    # Render the front end
    return render_template('workstation.html',
                           table=table,
                           data=data,
                           header=header,
                           info=info,
                           statistic_height=statistic_height)


def start(ip, port):

    global DATABASE

    # Connect the database from the engine.
    directory = Path(__file__).parents[2]
    DATABASE = str(directory) + '/SheffieldSolarCatalog/database/sql/ssc_sql.db'

    # Use gevent WSGI server instead of the Flask
    #http = WSGIServer((ip, port), app.wsgi_app, keyfile=str(directory) + '/certs/server.key', certfile=str(directory) + '/certs/server.crt')
    http = WSGIServer((ip, port), app.wsgi_app)
    
    # Start the server
    http.serve_forever()

    return 0
