from flask import Flask, render_template, request, g
from utility import Create_table, Create_live_plot, Query_info
from utility import Create_table, Query_info
import sqlite3
import numpy as np
import json
from bokeh.resources import INLINE

restore = "SELECT * FROM magnetogram_sunspot"
# DATABASE = '/Users/norbertgyenge/Research/SSC_py/Sheffield_Solar_Catalogues/database/sql/ssc_sql.db'
# DATABASE = 'E:/PythonDocs/SheffieldSolarCatalog/database/sql/ssc_sql.db'
DATABASE = '/Users/kevin/Documents/myProject/SolarCatalog_Kevin/web/flask_sqlite_query/static/database/sql/ssc_sql.db'


sd=''
ed=''
st=''
et=''
x=''
y=''
columns = 0
columns_all = 0
attributes = []
block_status = []
sunspot_type=''
order = ''
sql_attr = ''
sql_head = ''
sql_cmd = "SELECT * FROM magnetogram_sunspot"
header_all = []
header1 = []
header2 = []
header2_1 = []
header2_2 = []

app = Flask(__name__)

@app.before_request
def before_request():
    g.db = sqlite3.connect(DATABASE)


@app.teardown_request
def teardown_request(exception):
    if hasattr(g, 'db'):
        g.db.close()

@app.route('/')
def index():    
    return render_template('index.html')

@app.route('/help.html')
def help():    
    return render_template('help.html')

@app.route('/test.html', methods=['GET', 'POST'])
def query():

    # Save the previous SQL command
    global restore,sd,ed,sunspot_type,sql_cmd,data,st,et,columns,attributes,sql_attr,sql_head,block_status,header_all,header1,header2,columns_all,header2_1,header2_2,x,y


    # Check the request method
    if request.method == 'POST':
        if 'sunspot_type' in request.form:
            sql_attr = '' #clear attritubes
            sd = request.form['start_date']
            ed = request.form['end_date']
            st = request.form['start_time']
            et = request.form['end_time']
            order = request.form['order_by']
            attributes = request.values.getlist('attributes')
            block_status = [1,len(attributes)]
            # set sql head
            if len(attributes) == 0:
                sql_attr = '*'
            else:
                for a in range(len(attributes)):
                    sql_attr = sql_attr + attributes[a] + ','
                sql_attr = sql_attr + 'p_key'

            sql_head = 'SELECT ' + sql_attr + ' FROM '
            order_info = ' ORDER BY ' + order

            sunspot_type = request.form['sunspot_type']

            if sunspot_type == 'magnetogram':
                sunspot_type = "magnetogram_sunspot"
            elif sunspot_type == 'continuum':
                sunspot_type = "continuum_sunspot"



            if sd != '' and ed != '' :
                if st != '' and et != '' :
                    sql_cmd = sql_head + sunspot_type+" WHERE DATE_OBS >= '"+sd+"' AND "+"Time_obs >= '"+st+"' AND " +"DATE_OBS <= '"+ed+"' AND " + "Time_obs <= '"+et+"'" + order_info
                elif st == '' and et != '' :
                    sql_cmd = sql_head + sunspot_type+" WHERE DATE_OBS >= '"+sd+"' AND " +"DATE_OBS <= '"+ed+"' AND " + "Time_obs <= '"+et+"'" + order_info
                elif st != '' and et == '' :
                    sql_cmd = sql_head + sunspot_type+" WHERE DATE_OBS >= '"+sd+"' AND " +"Time_obs >= '"+st+"' AND " + "DATE_OBS <= '"+ed+"'" + order_info
                elif st == '' and et == '' :
                    sql_cmd = sql_head + sunspot_type+" WHERE DATE_OBS >= '"+sd+"' AND "+"DATE_OBS <= '"+ed+"'" + order_info
            elif sd != '' and ed == '' :
                if st != '' :
                    sql_cmd = sql_head + sunspot_type+" WHERE DATE_OBS >= '"+sd+"' AND "+"Time_obs >= '"+st+"'" + order_info
                elif st == '' :
                    sql_cmd = sql_head + sunspot_type+" WHERE DATE_OBS >= '"+sd+"'" + order_info
            elif sd == '' and ed != '' :
                if et != '' :
                    sql_cmd = sql_head + sunspot_type+" WHERE DATE_OBS <= '"+ed+"' AND "+"Time_obs <= '"+et+"'" + order_info
                elif et == '' :
                    sql_cmd = sql_head + sunspot_type+" WHERE DATE_OBS <= '"+ed+"'" + order_info
            else:
                sql_cmd = sql_head+sunspot_type+order_info

        # # New SQL command is applied and saved.
        # if 'sql_cmd' in request.form:
        #     sql_cmd = request.form['sql_cmd']
        #     restore = sql_cmd

        # # No new SQL command, restore the previous one.
        # if 'sql_cmd' not in request.form:
        #     sql_cmd = restore

        if "x" in request.form:
            # hist = request.form['test']
            hist = True
            x = request.form['x']
            y = request.form['y']

        if "x" not in request.form:
            hist = False

    else:
        sql_cmd = "SELECT * FROM magnetogram_sunspot"
        sql_attr = '*'
        hist = False

    # Send the query to sqlite
    sql_table = g.db.execute(sql_cmd)

    table, header = Create_table(sql_table)
    # Get the whole header in the complete table
    table_all_1, header_all_1 = Create_table(g.db.execute("SELECT * FROM magnetogram_sunspot"))
    table_all_2, header_all_2 = Create_table(g.db.execute("SELECT * FROM continuum_sunspot"))
    # if sql_attr=='*' and len(header_all)==0:
        # Divide header into two parts
    header1 = []
    header2 = []
    header2_1 = []
    header2_2 = []
    for index in xrange(0,len(header_all_1)):
        if index < 6:
            header1.append(header_all_1[index])
        elif index>=6 and index<16:
            header2.append(header_all_1[index])
        else:
            header2_1.append(header_all_1[index])

    for index in xrange(0,len(header_all_2)):
        if index >= 16:
            header2_2.append(header_all_2[index])

    columns = len(table[0])
    # columns_all = len(table_all_1[0])

    # Create data for downloading
    data=[]
    data=data+header

    for row in table:
        new_row = []+row
        new_row[0] = '\r\n'+str(row[0])
        data = data+new_row

    data = json.dumps(data)

    info = Query_info(table)

    if hist is not False:
        script, div = Create_live_plot(table, header, x,y)
        js_resources = INLINE.render_js()
        css_resources = INLINE.render_css()
        plot_status = 1

        return render_template('test.html', table=table,header1=header1,header2=header2,header2_1=header2_1,header2_2=header2_2,
                               header=header, sql=sql_cmd, script=script,plot_status=plot_status,
                               js_resources=js_resources, data=data,x=x,y=y,
                               css_resources=css_resources,columns=columns,
                               # columns_all=columns_all,
                               div=div, info=info, sd=sd, ed=ed,st=st,et=et,
                               sunspot_type=sunspot_type,block_status=block_status)

    return render_template('test.html', table=table,data=data,header1=header1,header2=header2,header2_1=header2_1,header2_2=header2_2,
                           header=header, sql=sql_cmd, info=info,columns=columns,
                           # columns_all=columns_all,
                           sd=sd,ed=ed,st=st,et=et,sunspot_type=sunspot_type,
                           block_status=block_status)


if __name__ == "__main__":
    app.run()
