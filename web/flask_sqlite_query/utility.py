import math
from bokeh.plotting import figure,show,output_file
import numpy as np
from bokeh.embed import components
# from bokeh.charts import Bar
TOOLS="hover,crosshair,pan,wheel_zoom,zoom_in,zoom_out,box_zoom,undo,redo,reset,tap,save,box_select,poly_select,lasso_select,"

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


def Create_live_histogram_plot(table, header, hist, weight):

    t = np.array(table)
    hist = t.T[header.index(hist)]

    if weight == 'None':
        histv, edges = np.histogram(hist, density=False)

    else:
        weight = t.T[header.index(weight)]
        histv, edges = np.histogram(hist, weights=weight, density=False)

    p = figure(tools=TOOLS)

    p.quad(top=histv, bottom=0, left=edges[:-1], right=edges[1:],
        fill_color="#036564", line_color="#033649")

    script, div = components(p)

    return script, div

def Create_live_2D_scatter_plot(table, header, x, y, c, s):
    import matplotlib as mpl
    import matplotlib.pyplot as plt

    t = np.array(table)

    x = t.T[header.index(x)]
    y = t.T[header.index(y)]

    if c == 'None':
        colors = ['#7800e2'] * len(x)

    else:
        c = t.T[header.index(c)]
        colors = ["#%02x%02x%02x" % (int(r), int(g), int(b))
                  for r, g, b, _ in 255*plt.cm.viridis(mpl.colors.Normalize()(c))]

    print x,y,s,c
    normalise_axis = (abs(max(x) - min(x)) + abs(max(y) - min(y))) / 100

    if s == 'None':
        radii = normalise_axis / 5

    else:
        s = t.T[header.index(s)]
        scaling = (s - min(s)) / (max(s) - min(s))
        radii = normalise_axis / 2 * scaling

    p = figure(tools=TOOLS)
    p.circle(x, y, radius=radii, fill_color=colors, fill_alpha=0.75)
    script, div = components(p)

    return script, div

def Create_live_2D_line_plot(table, header, xl, yl):

    t = np.array(table)

    xl = t.T[header.index(xl)]
    yl = t.T[header.index(yl)]

    p = figure(tools=TOOLS)
    p.line(xl, yl)
    script, div = components(p)

    return script, div
