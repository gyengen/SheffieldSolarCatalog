'''----------------------------------------------------------------------------

flask.py



----------------------------------------------------------------------------'''


from flask import Flask, render_template, request, g
from gevent.pywsgi import WSGIServer
from bokeh.resources import INLINE
from .python.live_plot import *
from .python.utility import *
from gevent import monkey
from pathlib import Path
import sqlite3
import json
import os

monkey.patch_all()

DATABASE = ''

# Define global variables --------------------------------------------------'''


class att:

    # consists of two boolean elements; the first one is whether the
    # front-end have accessed to the back-end; another is the number
    # of the columns in the table
    block_status = []

    # Default sql query command
    sql_cmd = "SELECT * FROM continuum_sunspot"

    # start date, end date, start time, end time
    sd, ed, st, et = '', '', '', ''

    # columns of the table
    columns = 0

    # rows of the table
    rows = 0

    # selected row id
    selected_row = 0

    # list of all attributes in the table
    attributes = []

    # sunspot type (umbra or penumbra)
    sunspot_type = ''

    # attribute that should be used in sort
    order = ''

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

class param:

    path_AR = ''

    path_full = ''

    row = []


# Define global variables --------------------------------------------------'''


app = Flask(__name__)

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
    mg_path = param.path_AR.replace('continuum', 'magnetogram')

    # Visualise the active region
    script, div = Extrapolation_visual(mg_path)

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


@app.route('/workstation.html', methods=['GET', 'POST'])
def query():

    # Default commands
    c1 = "SELECT * FROM continuum_sunspot"
    c2 = "SELECT * FROM magnetogram_sunspot"

    # Get the whole header in the complete table
    table_all_1, header_all_1 = Create_table(g.db.execute(c1))
    table_all_2, header_all_2 = Create_table(g.db.execute(c2))

    # css command
    statistic_height = 0

    # Check the request method
    if request.method == 'POST':

        # clear the error message
        error_message = ''

        if 'sunspot_type' in request.form:

            # clear attritubes
            att.sql_attr = ''

            # Define the investigated period
            att.sd = request.form['start_date']
            att.ed = request.form['end_date']
            att.st = request.form['start_time']
            att.et = request.form['end_time']

            # Sort by
            att.order = request.form['order_by']

            # Get the attributes from the form
            att.sql_values = ' '
            att.attributes = request.values.getlist('attributes')

            # Minimum and maximum values for filtering the data
            values_min_mag = request.values.getlist('values_min_magnetogram')
            values_max_mag = request.values.getlist('values_max_magnetogram')
            values_min_cont = request.values.getlist('values_min_continuum')
            values_max_cont = request.values.getlist('values_max_continuum')

            # Define block status
            att.block_status = [1, len(att.attributes)]

            # set sql head
            if len(att.attributes) == 0:
                att.sql_attr = '*'

            # Read the sql attributes
            else:
                for a in range(len(att.attributes)):
                    att.sql_attr = att.sql_attr + att.attributes[a] + ','
                att.sql_attr = att.sql_attr + 'p_key'

            # Construct the sql command
            att.sql_head = 'SELECT ' + att.sql_attr + ' FROM '
            order_info = ' ORDER BY ' + att.order

            # Read the sunspot type, umbra or penumbra
            att.sunspot_type = request.form['sunspot_type']

            # set the type of the sunspot in the query
            if att.sunspot_type == 'magnetogram':
                att.sunspot_type = "magnetogram_sunspot"
                att.header_all = header_all_1
                att.values_min = values_min_mag
                att.values_max = values_max_mag

            # set the type of the sunspot in the query
            elif att.sunspot_type == 'continuum':
                att.sunspot_type = "continuum_sunspot"
                att.header_all = header_all_2
                att.values_min = values_min_cont
                att.values_max = values_max_cont

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

            # If start date adnd time are not empty
            if att.sd != '' and att.ed != '':

                # If start time adnd time are not empty
                if att.st != '' and att.et != '':

                    # sql command
                    att.sql_cmd = att.sql_head + att.sunspot_type + \
                        " WHERE ((DATE_OBS > '" + att.sd + \
                        "' AND DATE_OBS <'" + att.ed + "') OR (DATE_OBS='" + \
                        att.sd + "' AND Time_obs>'" + att.st + \
                        "' AND DATE_OBS <'" + att.ed + "') OR (DATE_OBS>'" + \
                        att.sd + "' AND Time_obs<'" + att.et + \
                        "' AND DATE_OBS='" + att.ed + "'))" + \
                        att.sql_values + order_info

                # if start time is empty
                elif att.st == '' and att.et != '':

                    # sql command
                    att.sql_cmd = att.sql_head + att.sunspot_type + \
                        " WHERE DATE_OBS >= '" + att.sd + \
                        "' AND DATE_OBS <='" + att.ed + \
                        "' AND Time_obs <= '" + att.et + "'" + \
                        att.sql_values + order_info

                # if end time is not defined

                elif att.st != '' and att.et == '':

                    # sql command
                    att.sql_cmd = att.sql_head + att.sunspot_type + \
                        " WHERE DATE_OBS >= '" + att.sd + "' AND " + \
                        "Time_obs >= '" + att.st + "' AND " + \
                        "DATE_OBS <= '" + att.ed + "'" + att.sql_values + \
                        order_info

                # if end time and start time not defined
                elif att.st == '' and att.et == '':

                    # sql command
                    att.sql_cmd = att.sql_head + att.sunspot_type + \
                        " WHERE DATE_OBS >= '" + att.sd + "' AND " + \
                        "DATE_OBS <= '" + att.ed + "'" + att.sql_values + \
                        order_info

            # If ending date is not defined
            elif att.sd != '' and att.ed == '':

                # If start time is not empyt
                if att.st != '':

                    # sql command
                    att.sql_cmd = att.sql_head + att.sunspot_type + \
                        " WHERE DATE_OBS >= '" + att.sd + "' AND " + \
                        "Time_obs >= '" + att.st + "'" + att.sql_values + \
                        order_info

                # if start time is empty
                elif att.st == '':

                    # sql command
                    att.sql_cmd = att.sql_head + att.sunspot_type + \
                        " WHERE DATE_OBS >= '" + att.sd + "'" + \
                        att.sql_values + order_info

            # if end date is not empyt but start date is not defined
            elif att.sd == '' and att.ed != '':

                # end time is not empty
                if att.et != '':

                    # sql command
                    att.sql_cmd = att.sql_head + att.sunspot_type + \
                        " WHERE DATE_OBS <= '" + att.ed + "' AND " + \
                        "Time_obs <= '" + att.et + "'" + att.sql_values + \
                        order_info

                # end time is not defined
                elif att.et == '':

                    # sql command
                    att.sql_cmd = att.sql_head + att.sunspot_type + \
                        " WHERE DATE_OBS <= '" + att.ed + "'" + \
                        att.sql_values + order_info

            else:
                if att.sql_values == '' or att.sql_values == ' END':

                    # sql command
                    att.sql_cmd = att.sql_head + att.sunspot_type + order_info

                else:

                    # sql command
                    att.sql_cmd = att.sql_head + att.sunspot_type + \
                        " WHERE " + att.sql_values + order_info

    else:

        # Use the default sql command, display every sunspot
        att.sql_cmd = c1
        att.sql_attr = '*'

    # Clear sql_table
    sql_table = []

    # Send the query to sqlite
    try:

        # Execute the query
        sql_table = g.db.execute(att.sql_cmd)

    except Exception as e:

        # Error if sending failed
        error_message = error_message + \
            "<p> -- Error happened when retrieving data.<br></p><br>"

        # Construct the sql command
        att.sql_cmd = att.sql_head + att.sunspot_type + order_info

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
        error_message = error_message + \
            "<p> -- No data detected based on your filer.<br></p><br>"

        # Default sql command
        att.sql_cmd = att.sql_head + att.sunspot_type + order_info

        # Execute the command
        sql_table = g.db.execute(att.sql_cmd)

        # Create the data table
        table, header = Create_table(sql_table)

        # Read the lenght of the table
        att.columns = len(table[0])

        # Read the lenght of the table
        att.rows = len(table)

    # Divide header into two parts
    att.header1 = []
    att.header2 = []
    att.header2_1 = []
    att.header2_2 = []

    for index in range(0, len(header_all_1)):
        if index < 6:
            att.header1.append(header_all_1[index])
        elif index >= 6 and index < 16:
            att.header2.append(header_all_1[index])
        else:
            att.header2_1.append(header_all_1[index])

    for index in range(0, len(header_all_2)):
        if index >= 16:
            att.header2_2.append(header_all_2[index])

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

        # The index of the selected row
        att.selected_row = int(request.form['AR_ID'])

    # Define the selected row
    param.row = table[att.selected_row]

    # Define the filename of the associated image
    param.path_AR, param.path_full = html_image_path(param.row, os.getcwd())

    # NOAA = str(table[int(request.form['AR_ID'])][4])
    script_html, div_html = Create_live_AR(param.path_AR,
                                           param.path_full, table, param.row)

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
                error_message = error_message + \
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
                error_message = error_message + \
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
                error_message = error_message + \
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
                error_message = error_message + \
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
        list_length = len(att_plot.div_frame_list)
        if list_length != 0:
            position_left = []
            position_top = []
            for x in range(0, list_length):

                # Define the corners of the window
                left = 100 + 20 * x
                top = 20 * x
                position_left.append(left)
                position_top.append(top)

    # Render the front end
    return render_template('workstation.html',
                           table=table,
                           data=data,
                           header=header,
                           info=info,
                           header_all_1=header_all_1,
                           header_all_2=header_all_2,
                           statistic_height=statistic_height)


def start(ip, port, directory):

    global DATABASE

    if directory == 'default':

        # Connect the database from the engine.
        directory = Path(__file__).parent.parent
        DATABASE = str(directory) + '/database/sql/ssc_sql.db'

    else:
        DATABASE = directory + '/database/sql/ssc_sql.db'

    # Use gevent WSGI server instead of the Flask
    http = WSGIServer((ip, port), app.wsgi_app)

    # TODO gracefully handle shutdown
    http.serve_forever()

    # Run it
    app.run()

    return
