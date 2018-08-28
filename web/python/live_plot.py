import numpy as np
from bokeh.embed import components
from bokeh.plotting import figure
from scipy import stats
from bokeh.models import HoverTool
import pyfits
import sunpy.cm as cm

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









def Create_live_AR(full_path, NOAA):

    from bokeh.plotting import figure, show, output_file
    # Open the fits file
    hdulist = pyfits.open(full_path)

    # Save the data
    scidata = hdulist[0].data

    # Close the fits file
    hdulist.close()

    # Separate the different layers in the fits
    image = scidata[0]
    image_umbra = scidata[1]
    image_penumbra = scidata[2]

    # Define custom tools for this plot
    TOOLS = "crosshair,pan,wheel_zoom,zoom_in,zoom_out,box_zoom,undo,redo,reset,tap,save,box_select,poly_select,lasso_select,"

    left, bottom = 0, 0
    right, top = np.shape(image)[0], np.shape(image)[0]

    # Initialise the figure window
    p = figure(tools=TOOLS, plot_width=300, plot_height=265, sizing_mode='scale_both',
               x_range=(left, right), y_range=(bottom, top), match_aspect=True,
               tooltips=[("x", "$x"), ("y", "$y"), ("value", "@image")])

    from bokeh.colors import RGB
    from matplotlib import cm

    m_coolwarm_rgb = (255 * cm.coolwarm(range(256))).astype('int')
    coolwarm_palette = [RGB(*tuple(rgb)).to_hex() for rgb in m_coolwarm_rgb]


    p.image(image=[image], x=0, y=0, dw=right, dh=top, palette=coolwarm_palette)

    p.xaxis.axis_label = 'X'
    p.yaxis.axis_label = 'Y'

    p.title.text = 'AR' + NOAA

    from bokeh.models import LogColorMapper, BasicTicker, ColorBar

    print(int(np.min(image)))
    
    
    color_mapper = LogColorMapper(palette=coolwarm_palette, low=int(np.min(image)), high=int(np.max(image)))
    color_bar = ColorBar(color_mapper=color_mapper, ticker=BasicTicker(desired_num_ticks=5),
                         label_standoff=8, border_line_color=None, location=(0,0),
                         orientation="horizontal",major_label_text_font_size='10pt')

    p.add_layout(color_bar, 'below')

    script_html, div_html = components(p)

    return script_html, div_html




def Create_live_fulldisk(full_path):

    from bokeh.plotting import figure, show, output_file
    # Open the fits file
    hdulist = pyfits.open(full_path)

    # Save the data
    scidata = hdulist[1].data

    # Close the fits file
    hdulist.close()

    # Separate the different layers in the fits
    image = scidata

    # Define custom tools for this plot
    TOOLS = "crosshair,pan,wheel_zoom,zoom_in,zoom_out,box_zoom,undo,redo,reset,tap,save,box_select,poly_select,lasso_select,"

    print(np.shape(image))
    left, bottom = 0, 0
    right, top = np.shape(image)[0], np.shape(image)[0]

    # Initialise the figure window
    p = figure(tools=TOOLS, plot_width=300, plot_height=265, sizing_mode='scale_both',
               x_range=(left, right), y_range=(bottom, top), match_aspect=True,
               tooltips=[("x", "$x"), ("y", "$y"), ("value", "@image")])

    from bokeh.colors import RGB
    from matplotlib import cm

    m_coolwarm_rgb = (255 * cm.coolwarm(range(256))).astype('int')
    coolwarm_palette = [RGB(*tuple(rgb)).to_hex() for rgb in m_coolwarm_rgb]


    p.image(image=[image], x=0, y=0, dw=right, dh=top, palette=coolwarm_palette)

    p.xaxis.axis_label = 'X'
    p.yaxis.axis_label = 'Y'

    p.title.text = 'AR' + NOAA

    script_html, div_html = components(p)

    return script_html, div_html


