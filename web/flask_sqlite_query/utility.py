import math
from bokeh.plotting import figure,show,output_file
import numpy as np
from bokeh.embed import components
from scipy import stats
from bokeh.models import HoverTool

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


def Create_live_histogram_plot(table, header, hist_index, density, fit, bin_n, color):
    '''This funciton generates a histogram

    Parameters
    ----------
        table - Query table, list
        header - 
        hist - 
        density -
        fit -
        color - 

    Returns
    -------
        array - list of the basic information of the input table'
    '''

    t = np.array(table)
    hist = t.T[header.index(hist_index)]

    # Histogram calculation
    histv, edges = np.histogram(hist, density=False, bins=int(bin_n))
 
    # Error bar calculation
    yerrs = np.sqrt(histv)

    # Defining the centre of bins and bin width
    bin_centre = 0.5*(edges[1:]+edges[:-1])
    d_bin = edges[1] - edges[0]
    total = float(sum(histv))

    if density == 'yes':

        # Normalise the histogram and the error
        histv = histv/total/d_bin
        yerrs = yerrs/total/d_bin

    if fit != 'None':
        # find minimum and maximum of xticks, so we know
        # where we should compute theoretical distribution
        xmin, xmax = min(edges), max(edges)  
        lnspc = np.linspace(xmin, xmax, 1000)

        # lets try the normal distribution first
        if fit == 'Normal':
            
            # get mean and standard deviation 
            m, s = stats.norm.fit(hist)

            # Create legend
            legend = 'Normal ' + 'STD = ' + str(m) + ' ' + 'AVG = ' + str(s) + ')'

            # now get theoretical values in our interval
            pdf_fit = stats.norm.pdf(lnspc, m, s)

        if fit == 'Gamma':

            # Parameters for gamma distribution
            ag,bg,cg = stats.gamma.fit(hist)  

            # Fit the histogram
            pdf_fit = stats.gamma.pdf(lnspc, ag, bg,cg) 

        if fit == 'Beta':

            # Parameters for Beta distribution
            ab,bb,cb,db = stats.beta.fit(hist) 

            # Fit 
            pdf_fit = stats.beta.pdf(lnspc, ab, bb,cb, db) 

    # Convert the DPF to Frequency
    if density == 'no': pdf_fit = pdf_fit * total * d_bin

    # Plot window initialisation
    p = figure(tools=TOOLS, logo="grey", plot_width=600, plot_height=338, y_range=(0, max(histv) * 1.5))

    # plot the histogram
    p.quad(top=histv, bottom=0, left=edges[:-1], right=edges[1:], fill_color=color, line_color=None, alpha=0.45, legend="PDF")

    # plot the fit
    if fit != 'None':
        p.line(lnspc, pdf_fit, line_color='red', alpha=0.9, line_width=2, legend=legend)


    for i in range(len(histv)):
        x = bin_centre[i]
        y_low, y_high = histv[i] - (yerrs[i] / 2), histv[i] + (yerrs[i] / 2)
        x_left, x_right = x - (d_bin / 5), x + (d_bin / 5) 
        
        # Plot the error bars
        p.line((x, x), (y_low, y_high), color='black', alpha=0.5, line_width=1, legend='Error bars')
        p.line((x_left, x_right), (y_high, y_high), color='black', alpha=0.5, line_width=1)
        p.line((x_left, x_right), (y_low, y_low), color='black', alpha=0.5, line_width=1)


    # Fancy style
    p.grid.grid_line_color = "white"
    p.background_fill_color = "#e9ebee"
    p.xaxis.axis_label = str(hist_index)
    if density == 'yes': p.yaxis.axis_label = "PDF"
    else: p.yaxis.axis_label = "Frequency"


    # Bokeh script
    script, div = components(p)

    return script, div

def Create_live_2D_scatter_plot(table, header, x_index, y_index, c, s):
    import matplotlib as mpl
    import matplotlib.pyplot as plt

    t = np.array(table)

    x = t.T[header.index(x_index)]
    y = t.T[header.index(y_index)]

    if c == 'None':
        colors = ['#7800e2'] * len(x)

    else:
        c = t.T[header.index(c)]
        colors = ["#%02x%02x%02x" % (int(r), int(g), int(b))
                  for r, g, b, _ in 255*plt.cm.viridis(mpl.colors.Normalize()(c))]

    normalise_axis = abs(max(x) - min(x)) / 100

    if s == 'None':
        radii = normalise_axis

    else:
        s = t.T[header.index(s)]
        scaling = (s - min(s)) / (max(s) - min(s)) * 2
        radii = normalise_axis * scaling

    # Plot window initialisation
    p = figure(tools=TOOLS, logo="grey", plot_width=600, plot_height=338)

    #Plot the data
    p.circle(x, y, radius=radii, line_color=None, fill_color=colors, fill_alpha=0.75)

    # Fancy style
    p.grid.grid_line_color = "white"
    p.background_fill_color = "#e9ebee"
    p.xaxis.axis_label = str(x_index)
    p.yaxis.axis_label = str(y_index)

    script, div = components(p)

    return script, div

def Create_live_2D_line_plot(table, header, xl_index, yl_index, line_col):

    t = np.array(table)

    xl = np.array(t.T[header.index(xl_index)])
    yl = np.array(t.T[header.index(yl_index)])

    idx   = np.argsort(xl)
    xl = np.array(xl)[idx]
    yl = np.array(yl)[idx]

    # Plot window initialisation
    p = figure(tools=TOOLS, logo="grey", plot_width=600, plot_height=338)

    #Plot the data
    p.line(xl, yl, alpha=0.9, line_width=2, color = line_col)

    # Fancy style
    p.grid.grid_line_color = "white"
    p.background_fill_color = "#e9ebee"
    p.xaxis.axis_label = str(xl_index)
    p.yaxis.axis_label = str(yl_index)

    script, div = components(p)

    return script, div






def Create_live_bivariate_histogram_plot(table, header, v_index, w_index, biv_w_bin):

    # DEfine custom tools for this plot
    TOOLS = "crosshair,pan,wheel_zoom,zoom_in,zoom_out,box_zoom,undo,redo,reset,tap,save,box_select,poly_select,lasso_select,"
    
    # Convert the table to np array
    t = np.array(table)

    # Convert the variables
    v = t.T[header.index(v_index)]
    w = t.T[header.index(w_index)]
    v = v.astype(np.double)
    w = w.astype(np.double)

    # Normalisation
    v_norm = (v - min(v)) / (max(v) - min(v))
    w_norm = (w - min(w)) / (max(w) - min(w))

    # Initialise the figure window
    p = figure(match_aspect=True, tools=TOOLS, background_fill_color='#440154', plot_width=500, plot_height=500)
    p.grid.visible = False

    # Plot the bivariate histogram
    r, bins = p.hexbin(v_norm, w_norm, size=0.1, hover_color="pink", hover_alpha=0.8)

    # Define custom hover
    hover = HoverTool(tooltips=[("count", "@c"), ("(q,r)", "(@q, @r)")],
                      mode="mouse", point_policy="follow_mouse", renderers=[r])

    # Add the Hower to the figure
    p.add_tools(hover)

    # Fancy style
    p.xaxis.axis_label = 'Normalised ' + str(v_index) + ' (Min: ' + str(min(v)) + ' , ' + 'Max: ' + str(max(v)) + ')'
    p.yaxis.axis_label = 'Normalised ' + str(w_index) + ' (Min: ' + str(min(w)) + ' , ' + 'Max: ' + str(max(w)) + ')'



    script, div = components(p)

    return script, div



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





