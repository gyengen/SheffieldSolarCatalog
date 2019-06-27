import math


def Bokehscript(att_plot, div, script):

    # Div frame
    div_frame = '''
                    <div class="bokeh_plot draggable_window z-position" id = "''' + str(att_plot.plot_times) + '''">
                    <input type="hidden" name="bokeh" id = "plot''' + str(att_plot.plot_times) + '''" value = "''' + str(att_plot.plot_times) + '''">
                        <div class="windowBar" id = "bokeh_plot_windowBar">
                            <div class="control_buttons close_button" id="bokeh_plot_close_button''' + str(att_plot.plot_times) + '''"></div>
                            <div class="control_buttons minimum_button" id="bokeh_plot_minimum_button''' + str(att_plot.plot_times) + '''"></div>
                            <div class="windowTitle">
                                <p>''' + att_plot.plot_type + '''</p>
                            </div>
                        </div>
                        <div id="figure">''' + div + '''</div>
                    </div>
                '''

    # Minimalise the window
    div_minimize_block = '''
                        <div class ="window1" id="minimize_button''' + str(att_plot.plot_times) + '''">
                            <p>''' + att_plot.plot_type + '''</p>
                        </div>
                        '''

    # Create the pokeh script
    bokeh_script = \
        '''
        <script>
        $(function() {
            $("#bokeh_plot_minimum_button''' + str(att_plot.plot_times) + '''").click(function(){
                $("#''' + str(att_plot.plot_times) + '''").css('display','none');
                $("#minimize_button''' + str(att_plot.plot_times) + '''").css('display','table');
            });
            $("#bokeh_plot_close_button''' + str(att_plot.plot_times) + '''").click(function(){
                $("#''' + str(att_plot.plot_times) + '''").css('display','none');
                $("#minimize_button''' + str(att_plot.plot_times) + '''").css('display','none')
                $("#plot''' + str(att_plot.plot_times) + '''").removeAttr('name');
                var deleted_plots = document.cookie.replace(/(?:(?:^|.*;\s*)deleted_plots\s*\=\s*([^;]*).*$)|^.*$/, "$1");
                deleted_plots += ",''' + str(att_plot.plot_times) + '''";
                document.cookie ="deleted_plots=" + deleted_plots
            });
            $("#minimize_button''' + str(att_plot.plot_times) + '''").click(function(){
                $("#''' + str(att_plot.plot_times) + '''").css('display','block');
                $("#minimize_button''' + str(att_plot.plot_times) + '''").css('display','none')
            });
        });
        </script>
        ''' + script

    return div_frame, div_minimize_block, bokeh_script


def p_key_remover(table):
    ''' Delete the last column of the table. The last one contains the
    primary key, whicj should be hidden

    Parameter
    ---------
        table - SQLlite fetchall output

    Returns
    -------
        table - SQLlite fetchall output, removed last column'''

    return list(map(lambda row: row[:-1], table))


def create_header(table):
    ''' Create the header of the table and omit the last item, primary key.primary

    Parameter
    ---------
        table - SQLlite fetchall output

    Returns
    -------
        list - header of the table'''

    # Extract the heder items from the table
    header = list(map(lambda x: x[0], table.description))

    # Delete the last item, primary key.
    header = header[:-1]

    return header


def isInt(number):
    ''' Item integer checking

    Parameter
    ---------
        string - to check

    Returns
    -------
        bool - True if it is integer, False if it is not.'''

    if math.modf(float(number))[0] == 0:
        return True
    else:
        return False


def isFloat(string):
    ''' Item float checking

    Parameter
    ---------
        string - to check

    Returns
    -------
        bool - True if it is float, False if it is not.'''

    try:
        float(string)
        return True
    except:
        return False


def float_acc(row):
    '''Check every row and setup the new accuracy.

    Parameter
    ---------
        row - Query table row

    Returns
    -------
        row - Formatted Query table row'''

    # This is the new format for each row
    row_format = []

    # Iterate over the items of row
    for item in row:

        # Check the float item
        if isFloat(item):

            # If the item is float round it
            item = float(round(item, 2))

            # Check the integer item
            if isInt(item):

                # If the item is int no decimal
                item = int(item)

        # Append the new row
        row_format.append(item)

    return row_format


def formatting_items(table):
    ''' Set the new float accouracy.

    Parameter
    ---------
        table - SQLlite fetchall output

    Returns
    -------
        table - SQLlite fetchall output, shorter float numbers'''

    return list(map(float_acc, table))


def Create_table(table):
    ''' Create the table and header from the SQLite query

    Parameter
    ---------
        table - SQLite query output

    Returns
    -------
        table - Formatted publication ready table
        header - header items of the table'''

    # Save the new table header
    header = create_header(table)

    # Save the selected rows
    table = table.fetchall()

    # Remove primary key from the user interface
    table = p_key_remover(table)

    # Float accuracy
    table = formatting_items(table)

    return table, header

def Get_primary_key(table):
    ''' Get the primary key values from the SQLite query

    Parameter
    ---------
        table - SQLite query output
    Returns
    -------
        p_keys - list of the primary keys'''

    # Save the selected rows
    table = table.fetchall()

    p_keys = list(map(lambda row: row[-1], table))

    return p_keys


def Query_info(table):
    ''' Basic query information.

    Parameters
    ----------
        table - Query table, list

    Returns
    -------
        array - list of the basic information of the input table'''

    info = []

    # Number of rows
    info.append(len(table))

    # Number of columns
    info.append(len(table[0]))
    # Timespan

    return info



def keyword_check(form, string):
    '''Check the keyword in the request form.request

    Parameters
    ----------
        form - request.form from Flask
        key - keyword in the form
    Returns
    -------
        boolean - True if the keyword is present.'
    '''

    for keyword in form:
        if str(keyword) == string:
            return True

    return False

def pdf_image_path(row, directory):
    '''Build the full path of the observation based on html request to the pdf file.

    Parameters
    ----------
        row - HTML table tow
        directory - directory of the project

    Returns
    -------
        Filename of the associated pdf image of the row

    '''

    Noaa_number = row[4]
    obs_type = row[2]
    date = row[0]
    time = row[1]

    fname_AR = ('hmi.ssc.' + str(Noaa_number) + '.' + str(obs_type) + '.' +
                str(date).replace('-', '') + '_' + str(time).replace(':', '') +
                '.pdf')

    fname_full = ('hmi.ssc.fulldisk.' + str(obs_type) + '.' +

                  str(date).replace('-', '') + '_' +
                  str(time).replace(':', '') + '.fits')

    path = '/static/database/img/AR' + str(date) + '/pdf/'
    AR = path + fname_AR

    full = path + fname_full

    return AR, full

def png_image_path(row, directory):
    '''Build the full path of the observation based on html request to the png file.

    Parameters
    ----------
        row - HTML table tow
        directory - directory of the project

    Returns
    -------
        Filename of the associated png image of the row

    '''

    Noaa_number = row[4]
    obs_type = row[2]
    date = row[0]
    time = row[1]

    fname_AR = ('hmi.ssc.' + str(Noaa_number) + '.' + str(obs_type) + '.' +
                str(date).replace('-', '') + '_' + str(time).replace(':', '') +
                '.png')

    fname_full = ('hmi.ssc.fulldisk.' + str(obs_type) + '.' +

                  str(date).replace('-', '') + '_' +
                  str(time).replace(':', '') + '.fits')

    path = '/static/database/img/AR' + str(date) + '/png/'
    AR = path + fname_AR

    full = path + fname_full

    return AR, full


def html_image_path(row, directory):
    '''Build the full path of the observation based on html request.

    Parameters
    ----------
        row - HTML table tow
        directory - directory of the project

    Returns
    -------
        Filename of the associated image of the row

    '''

    Noaa_number = row[4]
    obs_type = row[2]
    date = row[0]
    time = row[1]

    fname_AR = ('hmi.ssc.' + str(Noaa_number) + '.' + str(obs_type) + '.' +
                str(date).replace('-', '') + '_' + str(time).replace(':', '') +
                '.fits')

    fname_full = ('hmi.ssc.fulldisk.' + str(obs_type) + '.' +
                  str(date).replace('-', '') + '_' +
                  str(time).replace(':', '') + '.fits')

    path = directory + '/web/static/database/img/AR' + str(date) + '/fits/'
    AR = path + fname_AR

    full = path + fname_full

    return AR, full
