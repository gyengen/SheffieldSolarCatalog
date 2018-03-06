from flask import Flask, render_template, request, g
from utility import Create_table, Create_live_plot, Query_info
from utility import Create_table, Query_info
import sqlite3
import numpy as np
from bokeh.resources import INLINE


restore = "SELECT * FROM continuum_sunspot"
DATABASE = '/Users/norbertgyenge/Research/SSC_py/Sheffield_Solar_Catalogues/database/sql/ssc_sql.db'
# DATABASE = 'E:/PythonDocs/SheffieldSolarCatalog/database/sql/ssc_sql.db'
sy = 0
sm = 0
sd = 0
ey = 0
em = 0
ed = 0
sql_index = 0


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
    global restore,sy,sm,sd,ey,em,ed,month_list,day_list,sql_index

    month_list = []
    for i in range(1, 13):
        if i < 10:
            month_list.append('0'+str(i))
        else:
            month_list.append(str(i))

    day_list = []
    for i in range(1, 32):
        if i < 10:
            day_list.append('0'+str(i))
        else:
            day_list.append(str(i))

    # Check the request method
    if request.method == 'POST':

        sy = request.form['start_date_year']
        sm = request.form['start_date_month']
        sd = request.form['start_date_day']
        ey = request.form['end_date_year']
        em = request.form['end_date_month']
        ed = request.form['end_date_day']
        sunspot_type = request.form['sunspot_type']

        if sunspot_type == 'magnetogram':
            sunspot_type = "magnetogram_sunspot"
        elif sunspot_type == 'continuum':
            sunspot_type = "continuum_sunspot"

        if int(ey) >= int(sy):
            if int(em) >= int(sm):
                if int(ed) >= int(sd):
                    sql_index = 1
                else:
                    sql_index = 2
            else:
                sql_index = 2
        else:
            sql_index = 2

        if sql_index == 1:
            start_date = sy+'-'+sm+'-'+sd
            end_date = ey+'-'+em+'-'+ed
            sql_cmd = "SELECT * FROM "+sunspot_type+" WHERE DATE_OBS >= '"+start_date+"' AND "+"DATE_OBS <= '"+end_date+"'"
        else:
            sql_cmd = "SELECT * FROM continuum_sunspot"
        # # New SQL command is applied and saved.
        # if 'sql_cmd' in request.form:
        #     sql_cmd = request.form['sql_cmd']
        #     restore = sql_cmd

        # # No new SQL command, restore the previous one.
        # if 'sql_cmd' not in request.form:
        #     sql_cmd = restore

        if 'test' in request.form:
            hist = request.form['test']

        if 'test' not in request.form:
            hist = False

    else:
        sql_cmd = "SELECT * FROM continuum_sunspot"
        hist = False

    # Send the query to sqlite
    sql_table = g.db.execute(sql_cmd)

    print sql_table

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
                               div=div, info=info, sy=int(sy),sm=sm,
                               sd=sd,ey=int(ey),em=em,ed=ed,month = month_list,
                               day = day_list,index = sql_index)

    return render_template('test.html', table=table,
                           header=header, sql=sql_cmd, info=info, sy=int(sy),sm=sm,
                           sd=sd,ey=int(ey),em=em,ed=ed,month = month_list,
                           day = day_list, index = sql_index)


if __name__ == "__main__":
    app.run()
