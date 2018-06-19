from utility import Create_table, Create_live_2D_scatter_plot,Create_live_histogram_plot, Create_live_2D_line_plot, Query_info, keyword_check, Create_live_bivariate_histogram_plot
from flask import Flask, render_template, request, g
from utility import Create_table, Query_info
from gevent.pywsgi import WSGIServer
from bokeh.resources import INLINE
from gevent import monkey
import numpy as np
import sqlite3
import json

monkey.patch_all()

restore = "SELECT * FROM magnetogram_sunspot"
# DATABASE = '/Users/norbertgyenge/Research/SSC_py/Sheffield_Solar_Catalogues/database/sql/ssc_sql.db'
# DATABASE = 'E:/PythonDocs/SheffieldSolarCatalog/database/sql/ssc_sql.db'
# DATABASE = '/Users/kevin/Documents/myProject/SolarCatalog_Kevin/web/flask_sqlite_query/static/database/sql/ssc_sql.db'
DATABASE = 'static/database/sql/ssc_sql.db'

sd=''   #start date
ed=''   #end date
st=''   #start time
et=''   #end time
x=''    # x-axis for scatter plot
y=''    # y-axis for scatter plot
columns = 0 #columns of the table
# columns_all = 0
attributes = [] # list of all attributes in the table
block_status = [] # consists of two boolean elements; the first one is whether the front-end have accessed to the back-end; another is the number of the columns in the table
sunspot_type='' #sunspot type
order = ''  #attribute that should be used in sort
sql_attr = ''   #list of attributes that should be included in the table
sql_head = ''   #first part of the query
sql_values = ' '    #one part of the query which is considered as the filter
sql_cmd = "SELECT * FROM magnetogram_sunspot"   #sql query
header_all = [] #all the headers in the table
header1 = []    #first 6 headers in the table
header2 = []    #the 6th to the 16th header in the table
header2_1 = []  #other attributes which are used in magnetogram exclude first 16 attributes
header2_2 = []  #other attributes wich are used in continuum exclude first 16 attributes
values_min = [] #minimum values for attributes
values_max = [] #maximum values for attributes
error_message = ''  #all the error message
plot_times = 0
div_frame_list = []
div_minimize_block_list = []
bokeh_script_list = []
bokeh_index_list = []

# message = ''    #some useful message for user

#set all attributes values to 0
for index in range(0,21):
    values_min.append(0)
    values_max.append(0)

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
    global restore,sd,ed,sunspot_type,sql_cmd,data,st,et,columns,attributes,sql_attr,sql_head,block_status,header_all,header1,header2,header2_1,header2_2,x,y
    global values_min,values_max,sql_values,error_message,plot_times,div_frame_list,div_minimize_block_list,bokeh_script_list,bokeh_index_list

    # Get the whole header in the complete table
    table_all_1, header_all_1 = Create_table(g.db.execute("SELECT * FROM magnetogram_sunspot"))
    table_all_2, header_all_2 = Create_table(g.db.execute("SELECT * FROM continuum_sunspot"))
    statistic_height = 0
    # Check the request method
    if request.method == 'POST':
        #clear the error message
        error_message = ''

        if 'sunspot_type' in request.form:
            sql_attr = '' #clear attritubes
            sd = request.form['start_date']
            ed = request.form['end_date']
            st = request.form['start_time']
            et = request.form['end_time']
            order = request.form['order_by']
            sql_values = ' '
            attributes = request.values.getlist('attributes')
            values_min_magnetogram = request.values.getlist('values_min_magnetogram')
            values_max_magnetogram = request.values.getlist('values_max_magnetogram')
            values_min_continuum = request.values.getlist('values_min_continuum')
            values_max_continuum = request.values.getlist('values_max_continuum')

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

            #set the type of the sunspot in the query
            if sunspot_type == 'magnetogram':
                sunspot_type = "magnetogram_sunspot"
                header_all = header_all_1
                values_min = values_min_magnetogram
                values_max = values_max_magnetogram
            elif sunspot_type == 'continuum':
                sunspot_type = "continuum_sunspot"
                header_all = header_all_2
                values_min = values_min_continuum
                values_max = values_max_continuum

            #set the range of attributes in the query
            for number in range(5,len(header_all)-1):
                min_value = values_min[number-5]
                max_value = values_max[number-5]
                if min_value == '':
                    min_value = '0'
                if max_value == '':
                    max_value = '0'

                try:
                    float(min_value)+float(max_value)
                except Exception as e:
                    error_message = error_message + "<p> -- Wrong input when setting attributes. ("+ header_all[number] +">> minimum:  "+ min_value +", maximum:  "+ max_value +")</p><br>"
                    continue

                if int(min_value) != 0 or int(max_value) != 0:
                    if int(min_value) < int(max_value):
                        sql_values = sql_values + header_all[number] + " >= " + min_value + " AND " + header_all[number] + " <= " + max_value + " AND "
                    elif int(min_value) > int(max_value):
                        error_message = error_message + "<p> -- Wrong input when setting attributes. ("+ header_all[number] +">> minimum:  "+ min_value +", maximum:  "+ max_value +")</p><br>"
            
            sql_values = sql_values + "END"
            sql_values = sql_values.replace("AND END","")

            if sd != '' and ed != '' :
                if st != '' and et != '' :
                    sql_cmd = sql_head + sunspot_type+" WHERE DATE_OBS >= '"+sd+"' AND "+"Time_obs >= '"+st+"' AND " +"DATE_OBS <= '"+ed+"' AND " + "Time_obs <= '"+et+"'" + sql_values + order_info
                elif st == '' and et != '' :
                    sql_cmd = sql_head + sunspot_type+" WHERE DATE_OBS >= '"+sd+"' AND " +"DATE_OBS <= '"+ed+"' AND " + "Time_obs <= '"+et+"'" + sql_values + order_info
                elif st != '' and et == '' :
                    sql_cmd = sql_head + sunspot_type+" WHERE DATE_OBS >= '"+sd+"' AND " +"Time_obs >= '"+st+"' AND " + "DATE_OBS <= '"+ed+"'" + sql_values + order_info
                elif st == '' and et == '' :
                    sql_cmd = sql_head + sunspot_type+" WHERE DATE_OBS >= '"+sd+"' AND "+"DATE_OBS <= '"+ed+"'" + sql_values + order_info
            elif sd != '' and ed == '' :
                if st != '' :
                    sql_cmd = sql_head + sunspot_type+" WHERE DATE_OBS >= '"+sd+"' AND "+"Time_obs >= '"+st+"'" + sql_values + order_info
                elif st == '' :
                    sql_cmd = sql_head + sunspot_type+" WHERE DATE_OBS >= '"+sd+"'" + sql_values + order_info
            elif sd == '' and ed != '' :
                if et != '' :
                    sql_cmd = sql_head + sunspot_type+" WHERE DATE_OBS <= '"+ed+"' AND "+"Time_obs <= '"+et+"'" + sql_values + order_info
                elif et == '' :
                    sql_cmd = sql_head + sunspot_type+" WHERE DATE_OBS <= '"+ed+"'" + sql_values + order_info
            else:
                if sql_values == ' ' or sql_values == ' END':
                    sql_cmd = sql_head+sunspot_type+order_info
                else:
                    sql_cmd = sql_head+sunspot_type+ " WHERE " +sql_values+order_info

        # # New SQL command is applied and saved.
        # if 'sql_cmd' in request.form:
        #     sql_cmd = request.form['sql_cmd']
        #     restore = sql_cmd

        # # No new SQL command, restore the previous one.
        # if 'sql_cmd' not in request.form:
        #     sql_cmd = restore

    else:
        sql_cmd = "SELECT * FROM magnetogram_sunspot"
        sql_attr = '*'

    sql_table = []
    # Send the query to sqlite
    try:
        sql_table = g.db.execute(sql_cmd)
    except Exception as e:
        error_message = error_message + "<p> -- Error happened when retrieving data.<br></p><br>"
        sql_cmd = sql_head+sunspot_type+order_info
        sql_table = g.db.execute(sql_cmd)
    
    table, header = Create_table(sql_table)

    try:
        columns = len(table[0])
    except Exception as e:
        error_message = error_message + "<p> -- No data detected based on your filer.<br></p><br>"
        sql_cmd = sql_head+sunspot_type+order_info
        sql_table = g.db.execute(sql_cmd)
        table, header = Create_table(sql_table)
        columns = len(table[0])

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

    # Create data for downloading
    data=[]
    data=data+header

    for row in table:
        new_row = []+row
        new_row[0] = '\r\n'+str(row[0])
        data = data+new_row

    data = json.dumps(data)

    try:
        statistic_height = len(table) * 26 + 43
    except Exception as e:
        statistic_height = 0
    

    info = Query_info(table)

    form = request.form
    if keyword_check(request.form, 'plot_type') is True:
        script = ''
        div = ''
        plot_type = ''
        plot_status = 0
        css_resources = ''
        js_resources = ''
        active_bokeh = []

        #plot attributes for line plot
        xl = request.form['xl']
        yl = request.form['yl']
        line_col = request.form['line_col']
        #plot attributes for scatter plot
        x = request.form['x']
        y = request.form['y']
        s = request.form['s']
        c = request.form['c']
        #plot attributes for histogram plot
        v = request.form['v']
        density = request.form['histogram_den']
        fit = request.form['histogram_fit']
        color = request.form['histogram_col']
        bin_n = request.form['histogram_bin']
        #plot attributes for bivariate histogram plot
        biv_v = request.form['biv_v']
        biv_w = request.form['biv_w']
        biv_w_bin = request.form['biv_w_bin']

        if request.form['plot_type'] == 'line':          

            try:
                script, div = Create_live_2D_line_plot(table, header, xl,yl, line_col)
            except Exception as e:
                error_message = error_message + "<p> -- Creating line plot failed.</p><br> <p>"+e.message+"</p><br>"
            else:
                plot_status = 1
                plot_type = "Line Plot"
                plot_times = plot_times + 1
            finally:
                js_resources = INLINE.render_js()
                css_resources = INLINE.render_css()

        elif request.form['plot_type'] == 'scatter_2d':            
            try:
                script, div = Create_live_2D_scatter_plot(table, header, x,y,c,s)
            except Exception as e:
                error_message = error_message + "<p> -- Creating scatter plot failed.</p><br> <p>"+e.message+"</p><br>"
            else:
                plot_status = 1
                plot_type = "Scatter Plot"
                plot_times = plot_times + 1
            finally:
                js_resources = INLINE.render_js()
                css_resources = INLINE.render_css()

        elif request.form['plot_type'] == 'histogram':           
            try:
                script, div = Create_live_histogram_plot(table, header, v, density, fit, bin_n, color)
            except Exception as e:
                error_message = error_message + "<p> -- Creating histogram plot failed.</p><br> <p>"+e.message+"</p><br>"
            else:
                plot_status = 1
                plot_type = "Histogram Plot"
                plot_times = plot_times + 1
            finally:
                js_resources = INLINE.render_js()
                css_resources = INLINE.render_css()

        elif request.form['plot_type'] == 'biv_hist':            

            try:
                script, div = Create_live_bivariate_histogram_plot(table, header, biv_v, biv_w, biv_w_bin)
            except Exception as e:
                error_message = error_message + "<p> -- Creating bivariate histogram plot failed.</p><br> <p>"+e.message+"</p><br>"
            else:
                plot_status = 1
                plot_type = "Bivariate Histogram"
                plot_times = plot_times + 1
            finally:
                js_resources = INLINE.render_js()
                ss_resources = INLINE.render_css()

        if plot_status == 1:
            div_frame = ''' 
                            <div class="bokeh_plot draggable_window z-position" id = "'''+str(plot_times)+'''">
                            <input type="hidden" name="bokeh" id = "plot'''+str(plot_times)+'''" value = "'''+str(plot_times)+'''">
                                <div class="windowBar" id = "bokeh_plot_windowBar">
                                    <div class="control_buttons close_button" id="bokeh_plot_close_button'''+str(plot_times)+'''"></div>
                                    <div class="control_buttons minimum_button" id="bokeh_plot_minimum_button'''+str(plot_times)+'''"></div>
                                    <div class="windowTitle">
                                        <p>'''+plot_type+'''</p>
                                    </div>
                                </div>
                                <div id="figure">'''+div+'''</div>
                            </div>
                        '''
            div_minimize_block = '''
                                <div class ="window1" id="minimize_button'''+str(plot_times)+'''">
                                    <p>'''+plot_type+'''</p>
                                </div>
                                '''   
            bokeh_script = '''
                            <script>
                            $(function() {
                                  $("#bokeh_plot_minimum_button'''+str(plot_times)+'''").click(function(){
                                    $("#'''+str(plot_times)+'''").css('display','none');
                                    $("#minimize_button'''+str(plot_times)+'''").css('display','table')
                                  });
                                  $("#bokeh_plot_close_button'''+str(plot_times)+'''").click(function(){
                                    $("#'''+str(plot_times)+'''").css('display','none');
                                    $("#minimize_button'''+str(plot_times)+'''").css('display','none')
                                    $("#plot'''+str(plot_times)+'''").removeAttr('name');
                                  });
                                  $("#minimize_button'''+str(plot_times)+'''").click(function(){
                                    $("#'''+str(plot_times)+'''").css('display','block');
                                    $("#minimize_button'''+str(plot_times)+'''").css('display','none')
                                  });
                            });
                            </script>
                            '''+script   
        else:
            div_frame = ''
            div_minimize_block = ''
            bokeh_script = ''

        active_bokeh = request.values.getlist('bokeh')

        if script != '' and div != '' and div_frame != '':
            div_frame_list.append(div_frame)
            div_minimize_block_list.append(div_minimize_block)
            bokeh_script_list.append(bokeh_script)
            bokeh_index_list.append(str(plot_times))
            active_bokeh.append(str(plot_times))

        new_div_frame_list = []
        new_div_minimize_block_list = []
        new_bokeh_script_list = []

        if active_bokeh !=[]:
            plot_status = 1
            for index in range(0,len(div_frame_list)):
                for active_index in active_bokeh:
                    if active_index == bokeh_index_list[index-1]:
                        new_div_frame_list.append(div_frame_list[index-1])
                        new_div_minimize_block_list.append(div_minimize_block_list[index-1])
                        new_bokeh_script_list.append(bokeh_script_list[index-1])
                        break

        else:
            new_div_frame_list = new_div_frame_list.append(div_frame_list[len(div_frame_list)-1])
            new_div_minimize_block_list = new_div_minimize_block_list.append(div_minimize_block_list[len(div_minimize_block_list)-1])
            new_bokeh_script_list = new_bokeh_script_list.append(bokeh_script_list[len(bokeh_script_list)-1])
                

        return render_template('test.html', table=table,header1=header1,header2=header2,header2_1=header2_1,header2_2=header2_2,
                               header=header, sql=sql_cmd, bokeh_script_list=new_bokeh_script_list,plot_status=plot_status,plot_type=plot_type,
                               js_resources=js_resources, data=data,biv_v=biv_v, biv_w=biv_w, biv_w_bin=biv_w_bin,error_message=error_message,
                               css_resources=css_resources,columns=columns,values_min = values_min,values_max=values_max,statistic_height = statistic_height,
                               div=div, info=info, sd=sd, ed=ed,st=st,et=et,header_all_1=header_all_1,header_all_2=header_all_2,
                               sunspot_type=sunspot_type,block_status=block_status,div_frame_list=new_div_frame_list,div_minimize_block_list=new_div_minimize_block_list)


    return render_template('test.html', table=table,data=data,header1=header1,header2=header2,header2_1=header2_1,header2_2=header2_2,
                           header=header, sql=sql_cmd, info=info,columns=columns,values_min = values_min,values_max=values_max,error_message=error_message,
                           sd=sd,ed=ed,st=st,et=et,sunspot_type=sunspot_type,header_all_1=header_all_1,header_all_2=header_all_2,statistic_height = statistic_height,
                           block_status=block_status)


if __name__ == "__main__":

    #Define the IP address
    ip = '143.167.4.88'

    # use gevent WSGI server instead of the Flask
    http = WSGIServer((ip, 5000), app.wsgi_app)

    # TODO gracefully handle shutdown
    http.serve_forever()
    app.run()