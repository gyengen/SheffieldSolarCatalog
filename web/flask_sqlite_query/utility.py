import math
from bokeh.plotting import figure
import numpy as np
from bokeh.embed import components
from bokeh.charts import Bar

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
    # table = p_key_remover(table)

    # Float accuracy
    table = formatting_items(table)

    return table, header


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


def Create_live_plot(table, header, hist):

    t = np.array(table)
    hist_test = t.T[header.index(hist)]

    histv, edges = np.histogram(hist_test, density=False, bins=10)

    # must give a vector of images
    p = Bar(histv, plot_width=800, plot_height=300)
    script, div = components(p)



    return script, div
