import numpy as np

from bokeh.plotting import figure, show, output_file

x = [1,2,3,4,5,6,7,8,9,10]
y = [8,4,1,7,4,2,0,6,8,2]
# N = 10
# x = np.random.random(size=N)
# y = np.random.random(size=N)
print x
# radii = np.random.random(size=N) * 1.5
radii = 0.1
colors = [
    "#%02x%02x%02x" % (int(r), int(g), 150) for r, g in zip(x,y)
]

print 5*x
print colors

TOOLS="hover,crosshair,pan,wheel_zoom,zoom_in,zoom_out,box_zoom,undo,redo,reset,tap,save,box_select,poly_select,lasso_select,"

p = figure(tools=TOOLS)

p.scatter(x, y, radius=radii,
          fill_color=colors, fill_alpha=0.6,
          line_color=None)

output_file("color_scatter.html", title="color_scatter.py example")

show(p)  # open a browser