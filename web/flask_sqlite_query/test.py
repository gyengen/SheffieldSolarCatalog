from flask import Flask, render_template, request, g
from utility import Create_table, Create_live_plot, Query_info
import sqlite3
import numpy as np
from bokeh.resources import INLINE


restore = "SELECT * FROM continuum_sunspot"
DATABASE = '/Users/norbertgyenge/Research/SSC_py/Sheffield_Solar_Catalogues/database/sql/ssc_sql.db'


app = Flask(__name__)

@app.before_request
def before_request():
    g.db = sqlite3.connect(DATABASE)


@app.teardown_request
def teardown_request(exception):
    if hasattr(g, 'db'):
        g.db.close()


@app.route('/test.html', methods=['GET', 'POST'])
def query():

    # Save the previous SQL command
    global restore

    # Check the request method
    if request.method == 'POST':

        # New SQL command is applied and saved.
        if 'sql_cmd' in request.form:
            sql_cmd = request.form['sql_cmd']
            restore = sql_cmd

        # No new SQL command, restore the previous one.
        if 'sql_cmd' not in request.form:
            sql_cmd = restore

        if 'test' in request.form:
            hist = request.form['test']

        if 'test' not in request.form:
            hist = False

    else:
        sql_cmd = "SELECT * FROM continuum_sunspot"
        hist = False

    # Send the query to sqlite
    sql_table = g.db.execute(sql_cmd)

    table, header = Create_table(sql_table)

    info = Query_info(table)

    if hist is not False:
        div, script = Create_live_plot(table, header, hist)
        js_resources = INLINE.render_js()
        css_resources = INLINE.render_css()

        return render_template('test.html', table=table,
                               header=header, sql=sql_cmd, script=script,
                               js_resources=js_resources,
                               css_resources=css_resources,
                               div=div, info=info)

    return render_template('test.html', table=table,
                           header=header, sql=sql_cmd, info=info)


if __name__ == "__main__":
    app.run()
