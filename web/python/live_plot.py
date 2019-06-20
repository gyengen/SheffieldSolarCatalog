from bokeh.models import BoxSelectTool, LassoSelectTool
from bokeh.models import LinearColorMapper, HoverTool
from bokeh.models import ColumnDataSource
from bokeh.models.markers import Triangle
from bokeh.embed import components
import scipy.ndimage.interpolation
from bokeh.plotting import figure
from bokeh.layouts import column
from bokeh.models import Label
from skimage import measure
from astropy.io import fits
import matplotlib as plt
from scipy import stats
import numpy as np
import sunpy.cm
import cv2
from datetime import datetime


TOOLS="hover,crosshair,pan,wheel_zoom,zoom_in,zoom_out,box_zoom,undo,redo,reset,tap,save,box_select,poly_select,lasso_select,"



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

    # Remove None if present
    hist = hist[hist != np.array(None)]


    # Histogram calculation
    histv, edges = np.histogram(hist, density=False, bins=int(bin_n))
    print(histv, edges)

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
            legend = 'Normal ' + 'STD = ' + str(round(m,2)) + ', ' + 'AVG = ' + str(round(s,2)) + ')'

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
    p = figure(tools=TOOLS, plot_width=650, plot_height=350, y_range=(0, max(histv) * 1.5), sizing_mode='scale_both')

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
    p.grid.grid_line_color = "#e9ebee"
    p.background_fill_color = "white"
    p.xaxis.axis_label = str(hist_index)
    p.border_fill_color = "#e9ebee"
    p.legend.label_text_font_size = '10pt'
    if density == 'yes': p.yaxis.axis_label = "PDF"
    else: p.yaxis.axis_label = "Frequency"


    # Bokeh script
    script, div = components(p)

    return script, div

def delete_nonetype_in_rows(data):
    new_data = []
    for x in data:
        if x != None:
            new_data.append(x)
    return new_data

def Create_live_2D_scatter_plot(table, header, x_index, y_index, c, s):
    import matplotlib as mpl
    import matplotlib.pyplot as plt

    t = np.array(table)

    x = delete_nonetype_in_rows(t.T[header.index(x_index)])
    y = delete_nonetype_in_rows(t.T[header.index(y_index)])

    if c == 'None':
        colors = ['#7800e2'] * len(x)

    else:
        colors = [c] * len(x)

    if (x_index == "Date_obs" or x_index == "Time_obs") or (y_index == "Date_obs" or y_index == "Time_obs"):
        #Convert strings to dates if required
        if (x_index == "Date_obs"):
            x = [datetime.strptime(date, '%Y-%m-%d').date() for date in x]
        elif (x_index == "Time_obs"):
            x = [datetime.strptime(date, '%H:%M:%S').date() for date in x]
        if (y_index == "Date_obs"):
            y = [datetime.strptime(date, '%Y-%m-%d').date() for date in y]
        elif (y_index == "Time_obs"):
            y = [datetime.strptime(date, '%H:%M:%S').date() for date in y]

        # Plot window initialisation
        if (x_index == "Date_obs" or x_index == "Time_obs") and (y_index == "Date_obs" or y_index == "Time_obs"):
            p = figure(tools=TOOLS,x_axis_type="datetime",y_axis_type="datetime", plot_width=600, plot_height=338)
        elif (x_index == "Date_obs" or x_index == "Time_obs"):
            p = figure(tools=TOOLS,x_axis_type="datetime",plot_width=600, plot_height=338)
        elif (y_index == "Date_obs" or y_index == "Time_obs"):
            p = figure(tools=TOOLS,y_axis_type="datetime",plot_width=600, plot_height=338)
        #Plot the data
        p.circle(x, y, line_color=None, fill_color=colors, fill_alpha=0.75)

    else:
        normalise_axis = abs(max(x) - min(x)) / 100

        if s == 'None':
            radii = normalise_axis

        else:
            s = t.T[header.index(s)]
            scaling = (s - min(s)) / (max(s) - min(s)) * 2
            radii = normalise_axis * scaling

        # Plot window initialisation
        p = figure(tools=TOOLS, plot_width=600, plot_height=338)

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

    xl = delete_nonetype_in_rows(t.T[header.index(xl_index)])
    yl = delete_nonetype_in_rows(t.T[header.index(yl_index)])

    #Convert strings to dates if required
    if (xl_index == "Date_obs"):
        xl = [datetime.strptime(date, '%Y-%m-%d').date() for date in xl]
    elif (xl_index == "Time_obs"):
        xl = [datetime.strptime(date, '%H:%M:%S').date() for date in xl]
    if (yl_index == "Date_obs"):
        yl = [datetime.strptime(date, '%Y-%m-%d').date() for date in yl]
    elif (yl_index == "Time_obs"):
        yl = [datetime.strptime(date, '%H:%M:%S').date() for date in yl]

    idx   = np.argsort(xl)
    xl = np.array(xl)[idx]
    yl = np.array(yl)[idx]

    # Plot window initialisation
    if (xl_index == "Date_obs" or xl_index == "Time_obs") and (yl_index == "Date_obs" or yl_index == "Time_obs"):
        p = figure(tools=TOOLS,x_axis_type="datetime",y_axis_type="datetime", plot_width=600, plot_height=338)
    elif (xl_index == "Date_obs" or xl_index == "Time_obs"):
        p = figure(tools=TOOLS,x_axis_type="datetime",plot_width=600, plot_height=338)
    elif (yl_index == "Date_obs" or yl_index == "Time_obs"):
        p = figure(tools=TOOLS,y_axis_type="datetime",plot_width=600, plot_height=338)
    else:
        p = figure(tools=TOOLS,plot_width=600, plot_height=338)

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

    # Define custom tools for this plot
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


def Generate_position_data(hdulist, hdulist_full):

    # Save the headers
    header = hdulist[0].header
    header_full = hdulist_full[0].header

    # The coordinates of the corners of ROI
    rx = np.array([int(header['BL_X']), int(header['TR_X'])])
    ry = np.array([int(header['BL_Y']), int(header['TR_Y'])])

    # From pixel to arcsecs
    rx = (rx - int(header_full['CRPIX1'])) * float(header_full['CDELT1'])
    ry = (ry - int(header_full['CRPIX2'])) * float(header_full['CDELT2'])

    # The dimensions of the ROI
    ny, nx = np.shape(hdulist[0].data)

    # Generate a arcsec meshgrid for the html visualisation
    xv, yv = np.meshgrid(np.linspace(rx[0], rx[1], nx),
                         np.linspace(ry[0], ry[1], ny),
                         indexing='xy')

    return xv, yv


def subpanel_live_plot(p, obs, table, selected_row):
    ''' Live histogram below the AR'''

    # Initialise the subpanel
    k = figure(tools="save",
               plot_width=300,
               plot_height=80)

    # Using smaller image to save computation time
    obs = scipy.ndimage.interpolation.zoom(obs,.5)

    # Flatten the image
    obs_flat = np.array(obs).flatten()

    # Save some memory
    obs_flat = np.array(obs_flat, dtype="f4")

    # Remove NaN's
    obs_flat = obs_flat[~np.isnan(obs_flat)]

    # Calculate the histogram, removing NaN if present
    hist, edges = np.histogram(obs_flat, bins='rice')

    # Covert to logarithmic scale
    hist = np.log(hist)

    # Replace inf
    hist[np.isneginf(hist)] = 0

    # Define the range between minimum and maximum B
    B_minimum_inx = np.abs(edges[:-1] - float(selected_row[18])).argmin()
    B_maximum_inx = np.abs(edges[:-1] - float(selected_row[19])).argmin()

    # Define the selected range
    B_selected_range_x = edges[B_minimum_inx:B_maximum_inx]
    B_selected_range_y = hist[B_minimum_inx:B_maximum_inx]

    # Save the penumbra or umbra id
    if selected_row[3] == 'umbra':
        B_selected_umbra = [int(selected_row[5])]
        B_selected_penumbra = [0]

    elif selected_row[3] == 'penumbra':
        B_selected_umbra = [0]
        B_selected_penumbra = [int(selected_row[5])]

    # The date to be plotted
    source = ColumnDataSource({'top': hist, 'left': edges[:-1],
                               'right': edges[1:],
                               'umbra': ["-"] * len(hist),
                               'penumbra': ["-"] * len(hist)})

    source_s = ColumnDataSource({'top': B_selected_range_y[:-1],
                                 'left': B_selected_range_x[:-1],
                                 'right': B_selected_range_x[1:],
                                 'umbra': (B_selected_umbra *
                                           len(B_selected_range_y[:-1])),
                                 'penumbra': (B_selected_penumbra *
                                              len(B_selected_range_y[:-1]))})

    # Plot the histogram B
    k.quad(source=source, top='top', bottom=0, left='left', right='right',
           fill_color="#5d5d5d", line_color="#5d5d5d")

    # Plot the histogram B with the selected range
    k.quad(source=source_s, top='top', bottom=0, left='left', right='right',
           fill_color="#b72130", line_color="#b72130")

    # Store the sunspot positions in arrays
    spot_x, spot_y = [], []

    # Save the umbra and penumbra id
    umbra, penumbra = [], []

    # Read the sunspot intensity position in the histogram from the table
    for row in table:

        # The selected sunspot
        if(row[3] == selected_row[3] and
           row[4] == selected_row[4] and
           row[5] == selected_row[5]):

            # The x coordinate
            spot_s_x = [float(row[17])]

            # The closest y coordinate
            spot_s_y = [hist[np.abs(edges[:-1] - float(row[17])).argmin()] +
                        hist.max() * 0.2]

            if str(row[3]) == 'umbra':

                # Umbra id
                umbra_s = [int(row[5])]

                # Penumbra id
                penumbra_s = [0]

            if str(row[3]) == 'penumbra':

                # Umbra id
                umbra_s = [0]

                # Penumbra id
                penumbra_s = [int(row[5])]

        # The other sunspots
        else:

            if row[17] == None:
               row[17] = np.nan 

            # The x coordinate
            spot_x.append(float(row[17]))

            # The closest y coordinate
            spot_y.append(hist[np.abs(edges[:-1] - float(row[17])).argmin()] +
                          hist.max() * 0.125)

            if str(row[3]) == 'umbra':

                # Umbra id
                umbra.append(int(row[5]))

                # Penumbra id
                penumbra.append(0)

            if str(row[3]) == 'penumbra':

                # Umbra id
                umbra.append(0)

                # Penumbra id
                penumbra.append(int(row[5]))

    # Convert the data to Bokeh compatible source object
    source = ColumnDataSource(dict(x=spot_x, y=spot_y,
                                   umbra=umbra, penumbra=penumbra))

    source_s = ColumnDataSource(dict(x=spot_s_x, y=spot_s_y,
                                     umbra=umbra_s, penumbra=penumbra_s))

    # Create the blue triangles
    glyph1 = Triangle(x="x", y="y", size=8, line_color=None,
                      line_width=0, fill_color='#4b82a5', angle=3.14)

    # Create the red triangle, indicating the selected sunspot
    glyph2 = Triangle(x="x", y="y", size=12, line_color=None,
                      line_width=0, fill_color='#b72130', angle=3.14)

    # Add them to the actual plot
    #k.add_glyph(source, glyph1)
    k.add_glyph(source_s, glyph2)

    # Hide the axis
    k.yaxis.visible = False

    # Custom hover tooltips
    hover = HoverTool(tooltips=[('B', '$x{1.11} G'),
                                ('lg(F)', '$y')])
    # Add the hover tool to the figure
    k.add_tools(hover)

    return k


def Extrapolation_visual(obs):

    # Define custom tools for this plot
    y1, x1 = 0, 0
    y2, x2 = np.shape(obs)[0], np.shape(obs)[1]

    # Setup the dimensions
    plot_width = 600
    plot_height = int((600. / x2) * y2)

    # Define the toolbox for the HTML image visualisation
    TOOLS = "crosshair,pan,zoom_in,zoom_out,box_select,lasso_select,reset,save"

    # Initialise the figure window
    p = figure(tools=TOOLS,
               plot_width=plot_width,
               plot_height=plot_height,
               sizing_mode='scale_both',
               x_range=(x1, x2),
               y_range=(y1, y2),
               toolbar_location="right")

    p.select(BoxSelectTool).select_every_mousemove = False
    p.select(LassoSelectTool).select_every_mousemove = False

    # Define the colormap
    exp_cmap = LinearColorMapper(palette='Greys256',
                                 nan_color='black')

    # Define the data
    data = dict(original=[obs],
                x=[0],
                y=[0],
                dw=[x2],
                dh=[y2])

    # Plot the AR image
    img = p.image(source=data, image='original', x='x', y='y',
                  dw='dw', dh='dh', color_mapper=exp_cmap)

    TOOLTIPS = [("B", "@original")]

    # Add the hover TOOLTIPS for the plot
    p.add_tools(HoverTool(renderers=[img], tooltips=TOOLTIPS))

    # Hide the axis
    p.yaxis.visible = False
    p.xaxis.visible = False

    # Generate the html and js scripts
    script_html, div_html = components(p)

    return script_html, div_html


def Create_live_AR(path_AR, path_full, table, selected_row):

    # Open the fits file, AR
    hdulist = fits.open(path_AR)

    # Open the fits file, full disk
    hdulist_full = fits.open(path_full)

    # Fix the broken fits
    hdulist.verify('fix')

    # Fix the broken fits
    hdulist_full.verify('fix')

    # Save the data
    obs = np.array(hdulist[0].data, dtype="f4")
    image_umbra = np.array(hdulist[1].data, dtype="f4")
    image_penumbra = np.array(hdulist[2].data, dtype="f4")
    b_mask = np.array(hdulist[3].data, dtype="f4")
    l_mask = np.array(hdulist[4].data, dtype="f4")
    
    if "magnetogram" in path_AR:
        obs_type = 'mag'

    elif "continuum" in path_AR:
        obs_type = 'con'

    else:
        obs_type = 'gen'

    if obs_type is 'mag':

        # Change the colormap
        palette = 'Greys256'

        # Normalise the data between -1 and 1.
        normalised = (2 * (obs - np.nanmin(obs)) /
                      (np.nanmax(obs) - np.nanmin(obs))) - 1

        # Minimum and maximum for colormap
        low = -1
        high = 1

        # Custom tooltips setup for the html
        TOOLTIPS = [("Lat, LCM", "@lat, @lon"),
                    ("X, Y", "@asec_x{1.11}, @asec_y{1.11}"),
                    ("PID/UID", "@umbra/@penumbra"),
                    ("B", "@original")]

    if obs_type is 'con':

        # Change the colormap
        colormap = sunpy.cm.get_cmap('sdoaia171')
        palette = [plt.colors.rgb2hex(m)
                   for m in colormap(np.arange(colormap.N))]

        # Normalise the data between 0 and 1.
        normalised = (obs - np.nanmin(obs)) / (np.nanmax(obs) - np.nanmin(obs))

        # Minimum and maximum for colormap
        low = 0
        high = 1

        # Custom tooltips setup for the html
        TOOLTIPS = [("Lat, LCM", "@lat, @lon"),
                    ("X, Y", "@asec_x{1.11}, @asec_y{1.11}"),
                    ("PID/UID", "@umbra/@penumbra"),
                    ("P", "@original")]

    if obs_type is 'gen':

        # Change the colormap
        palette = 'Magma256'

        # Normalise the data between -1 and 1.
        normalised = (obs - np.nanmin(obs)) / (np.nanmax(obs) - np.nanmin(obs))

    # Define custom tools for this plot
    y1, x1 = 0, 0
    y2, x2 = np.shape(obs)[0], np.shape(obs)[1]


    # Setup the dimensions
    plot_width = 300
    plot_height = 200

    # Calculate the positions in arcsecs
    asec_x, asec_y = Generate_position_data(hdulist, hdulist_full)

    # Close the fits files
    hdulist.close()
    hdulist_full.close()

    # Define the toolbox for the HTML image visualisation
    TOOLS = "pan,zoom_in,zoom_out,save"

    # Set the X and Y ranges for the plot
    if (x2 / y2) <= 1.5:

       # Picture is stretched into y dimension, cropping only y
       rx1, rx2 = x1, x2

       # New y range
       ry1 = (y2 - (rx2 / 1.5)) / 2
       ry2 = y2 - ((y2 - (rx2 / 1.5)) / 2)

    else:

       # Picture is stretched into x dimension, cropping only x
       ry1, ry2 = y1, y2

       # New y range
       rx1 = (x2 - (ry2 * 1.5)) / 2
       rx2 = x2 - ((x2 - (ry2 * 1.5)) / 2)

    # Initialise the figure window
    p = figure(tools=TOOLS,
               plot_width=plot_width,
               plot_height=plot_height,
               x_range=(rx1, rx2),
               y_range=(ry1, ry2),
               toolbar_location="right")

    p.select(BoxSelectTool).select_every_mousemove = False
    p.select(LassoSelectTool).select_every_mousemove = False

    # Define the colormap
    exp_cmap = LinearColorMapper(palette=palette,
                                 nan_color='black',
                                 low=low,
                                 high=high)

    # Define the data
    data = dict(image=[normalised],
                original=[obs],
                lat=[b_mask],
                lon=[l_mask],
                asec_x=[asec_x],
                asec_y=[asec_y],
                umbra=[image_umbra],
                penumbra=[image_penumbra],
                x=[0],
                y=[0],
                dw=[x2],
                dh=[y2])

    # Plot the AR image
    img = p.image(source=data, image='image', x='x', y='y',
                  dw='dw', dh='dh', color_mapper=exp_cmap)

    # Add the hover TOOLTIPS for the plot
    p.add_tools(HoverTool(renderers=[img], tooltips=TOOLTIPS))

    # Hide the axis
    p.yaxis.visible = False
    p.xaxis.visible = False

    # Find the contours in the umbra map, useing a binary mask
    c1 = measure.find_contours(np.where(image_umbra != 0, 1, 0), 0.5)

    # Plot the umbra contours
    for n, contour in enumerate(c1):
        p.line(contour[:, 1], contour[:, 0])

    # Find the contours in the umbra map, useing a binary mask
    c2 = measure.find_contours(np.where(image_penumbra != 0, 1, 0), 0.5)

    # Plot the umbra contours
    for n, contour in enumerate(c2):
        p.line(contour[:, 1], contour[:, 0])

    # Find the user selected sunspot from the html form
    if str(selected_row[3]) == 'umbra':
        selected_mask = np.where(image_penumbra == int(selected_row[5]), 1, 0)

    elif str(selected_row[3]) == 'penumbra':
        selected_mask = np.where(image_penumbra == int(selected_row[5]), 1, 0)

    # Plot the umbra contours
    for n, contour in enumerate(measure.find_contours(selected_mask, 0.5)):
        p.line(contour[:, 1], contour[:, 0], color='red')

    # Create the subpanel for the histogram
    k = subpanel_live_plot(p, obs, table, selected_row)

    # Arrange the two panels above and below
    p = column(p, k, sizing_mode='scale_width')

    # Generate the html and js scripts
    script_html, div_html = components(p)

    return script_html, div_html


def Create_header_table(header):
    header_list = []
    for i, key in enumerate(header):
        header_list.append(str(key) + ' = ' + str(header[i]))

    header_list = np.array(header_list)
    header_list.resize((33, 3))
    return header_list


def Create_live_fulldisk(full_path, selected_row, full):
    '''This funciton generates the fulldisk image for the html frontend

    Parameters
    ----------
        full_path - The full path of the observation

    Returns
    -------
        script_html - The associated javascript
        div_html - The actual image
    '''

    # Scale down the observation for faster downloading
    if full is True:
       scale = 1
    else:
       scale = 0.25

    if "magnetogram" in full_path:
        obs_type = 'mag'

    elif "continuum" in full_path:
        obs_type = 'con'

    else:
        obs_type = 'gen'

    # Try again and
    hdulist = fits.open(full_path, uint=True)

    # Fix the broken fits
    hdulist.verify('fix')

    # Save the data
    obs = np.array(hdulist[0].data, dtype="f4")

    # Save the header, index zero is an empty hdu
    header = hdulist[0].header

    # Close the fits file
    hdulist.close()

    if full is True:
        # Save the header table for the full disk htlm page
        header_table = Create_header_table(header)

    # Some parameters for the data to world conversion
    dx = float(header['CDELT1'])
    dy = float(header['CDELT2'])
    c_x = int(header['CRPIX1'])
    c_y = int(header['CRPIX2'])

    x_dim = int(np.shape(obs)[0])
    y_dim = int(np.shape(obs)[1])

    xasec, yasec = np.meshgrid((np.linspace(0, x_dim, x_dim) - c_x) * dx,
                               (np.linspace(0, y_dim, y_dim) - c_y) * dy)

    # New dimensions
    new_x = int(x_dim)
    new_y = int(y_dim)

    if obs_type is 'mag':

        # Change the colormap
        palette = 'Greys256'

        # Normalise the data between -1 and 1.
        normalised = (2 * (obs - np.nanmin(obs)) /
                      (np.nanmax(obs) - np.nanmin(obs))) - 1

        # Minimum and maximum for colormap
        low = -.25
        high = .25

        # Custom tooltips setup for the html
        TT = [("x, y", "@x_arcsec\", @y_arcsec\""), ("B", "@original G")]

    if obs_type is 'con':

        # Change the colormap
        colormap = sunpy.cm.get_cmap('sdoaia171')
        palette = [plt.colors.rgb2hex(m)
                   for m in colormap(np.arange(colormap.N))]

        # Normalise the data between 0 and 1.
        normalised = (obs - np.nanmin(obs)) / (np.nanmax(obs) - np.nanmin(obs))

        # Minimum and maximum for colormap
        low = 0
        high = 1

        # Custom tooltips setup for the html
        TT = [("x, y", "@x_arcsec\", @y_arcsec\""), ("P", "@original")]

    if obs_type is 'gen':

        # Change the colormap
        palette = 'Magma256'

        # Normalise the data between -1 and 1.
        normalised = (obs - np.nanmin(obs)) / (np.nanmax(obs) - np.nanmin(obs))
    

    normalised = scipy.ndimage.interpolation.zoom(normalised, scale)
    obs = scipy.ndimage.interpolation.zoom(obs, scale)
    xasec = scipy.ndimage.interpolation.zoom(xasec, scale)
    yasec = scipy.ndimage.interpolation.zoom(yasec, scale)

    xasec = np.array(xasec, dtype="f4")
    yasec = np.array(yasec, dtype="f4")
    obs = np.array(obs, dtype="f4")
    normalised = np.array(normalised, dtype="f4")

    # Define the data
    data = dict(image=[normalised],
                original=[obs],
                x_arcsec=[xasec],
                y_arcsec=[yasec],
                x=[0],
                y=[0],
                dw=[np.shape(obs)[0]],
                dh=[np.shape(obs)[1]])

    exp_cmap = LinearColorMapper(palette=palette,
                                 low=low,
                                 high=high,
                                 nan_color='black')
    
    TOOLS = "pan,zoom_in,zoom_out,reset,save"

    # Initialise the figure window
    p = figure(tools=TOOLS,
               plot_width=300,
               plot_height=280,
               sizing_mode='scale_both',
               x_range=(0, np.shape(obs)[0]),
               y_range=(0, np.shape(obs)[1]),
               match_aspect=True,
               toolbar_location="left")

    # Plot the full disk image
    l1 = p.image(source=data, image='image', x='x', y='y',
                 dw='dw', dh='dh', color_mapper=exp_cmap)

    # Add the hover TOOLTIPS for the plot 
    hover = HoverTool(renderers=[l1], tooltips=TT)
    p.add_tools(hover)

    # Read the NOAA numbers from the header
    NOAA_list = str(header['ARS']).split(",")

    # Define the header index ('ARS' record in header) of the selected AR
    index = NOAA_list.index(str(selected_row[4]))

    for i in range(len(NOAA_list)):

        # Highlight the selected active region
        if i == index:
            color = '#b91e2c'
        else:
            color = '#0e0400'

        # Extract the corner cordinates from the header
        top = int(float(header['TR_Y'].split(",")[i]) * scale) 
        bottom = int(float(header['BL_Y'].split(",")[i]) * scale)
        left = int(float(header['BL_X'].split(",")[i]) * scale)
        right = int(float(header['TR_X'].split(",")[i]) * scale)

        # Plot the ROI region
        p.quad(top=top, bottom=bottom, left=left, right=right,
               fill_alpha=0, line_color=color, line_width=0.5)

        # Adding annotations for the all AR
        p.add_layout(Label(x=left, y=top, text=' ' + str(NOAA_list[i]) + ' ',
                           background_fill_color=color,
                           background_fill_alpha=1,
                           border_line_alpha=0,
                           text_font_size="10pt",
                           text_color="#ededed"))

    # Hide the axis
    p.yaxis.visible = False
    p.xaxis.visible = False

    # Generating the script for the html
    script_html, div_html = components(p)

    if full is False:
        return script_html, div_html

    if full is True:
        return script_html, div_html, header_table

