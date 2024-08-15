from datetime import datetime, date
from io import BytesIO
import webbrowser
import calendar
import threading
import os

import pandas as pd
from flask import Flask, request, redirect, url_for, render_template, send_file 


from scheduling import *

DEPARTMNT = 0
EMPLOYEE = 1
SAVE_PATH = f"{os.getcwd()}/reusable_data"

year = -1
month = 7
last_month = 0 #是否接續上個月

format = None
my_schedual = None

app = Flask(__name__)



@app.route('/', methods=['GET', 'POST'])
def home():
    global year, month, format, my_schedual
    if request.method == 'GET':
        
        if os.path.exists(SAVE_PATH) == False:
            os.mkdir(SAVE_PATH)

        file_names = os.listdir(SAVE_PATH)
        now = datetime.now()
        return render_template('home.html', default_data={"year" : str(now.year), "file_names" : file_names})
    else:
        year = int(request.form['year'])
        month = int(request.form['month'])
        reusable_data_path = f"{SAVE_PATH}/{request.form['reusable_data']}"
        
        format = SchedualFormat(day_nums=calendar.monthrange(year, month)[1], period=2, \
                                start_day=(date(year, month, 1).weekday() + 1 ) % 7, period_name=["上午", "下午"])
        format.set_manpower_in_week(week_day=6, manpower=0, period=[1])
        format.set_manpower_in_week(week_day=7, manpower=0, period=[0, 1])

        my_schedual = ScheduleContainer(format)
        if request.form['reusable_data'] != "(":
            my_schedual.load_reusable_data(reusable_data_path)
        return redirect(url_for('show_status'))

@app.route('/show_status')
def show_status():
    if my_schedual == None:
        return redirect(url_for('home'))

    global month
    return render_template('show_status.html', employees=my_schedual.get_employee_json(), \
                           departments=my_schedual.get_department_json(), target_class=EMPLOYEE, 
                           title=f"{year}年 {month}月 班表")


@app.route('/edit/<int:target_class>/<int:id>', methods=['GET', 'POST'])
def edit(target_class, id):
    if my_schedual == None:
        return redirect(url_for('home'))
    if target_class == EMPLOYEE:
        if request.method == 'GET':
            target = my_schedual.employees[id]
            origin = {'name' : target.name, 'room' : target.start_department, \
                      'hate_period' : target.hate_period_input, \
                      'personal_leave' : target.personal_leave_input, \
                        'bind_period' : target.bind_period_input}
            return render_template('employee_form.html', title="編輯員工資訊", origin=origin, \
                                   post_url=url_for('edit', target_class=target_class, id=id), \
                                    firstDayOfWeek=format.start_day, daysInMonth=format.day_nums)
        else:
            my_schedual.employees[id] = my_schedual.set_employee_data(request.form)
            

    else:
        if request.method == 'GET':
            target = my_schedual.departments[id]
            origin = {'name' : target.name,'man_power' : target.man_power_input,'rest_time' : target.rest_time_input}
            return render_template('department_form.html', title="編輯診間資訊", origin=origin, \
                                   post_url=url_for('edit', target_class=target_class, id=id))
        else:
            my_schedual.departments[id] = my_schedual.set_department_data(request.form)


    return redirect(url_for('show_status')) 

@app.route('/delete/<int:target_class>/<int:id>')
def delete(target_class, id):
    if my_schedual == None:
        return redirect(url_for('home'))
    if target_class == EMPLOYEE:
        my_schedual.employees.pop(id)
    else:
        my_schedual.departments.pop(id)
    return redirect(url_for('show_status'))
    
@app.route('/add_employee', methods=['GET', 'POST'])
def add_employee():
    if my_schedual == None:
        return redirect(url_for('home'))
    
    global year, month
    if request.method == 'GET':
        origin = {'name' : '', 'room' : '', 'hate_period' : '', 'personal_leave' : '', 'bind_period' : ''}
        return render_template('employee_form.html', title="新增員工", origin=origin, \
                               post_url=url_for('add_employee'), \
                                    firstDayOfWeek=format.start_day, daysInMonth=format.day_nums)
    else:
        new_employee = my_schedual.set_employee_data(request.form)
        my_schedual.employees.append(new_employee)

        return redirect(url_for('show_status'))



@app.route('/add_department', methods=['GET', 'POST'])
def add_department():
    if my_schedual == None:
        return redirect(url_for('home'))
    
    if request.method == 'GET':
        origin = {'name' : '', 'man_power' : '', 'rest_time' : ''}
        return render_template('department_form.html', origin=origin, title="新增診間")
    else:
        new_department = my_schedual.set_department_data(request.form)
        my_schedual.departments.append(new_department)
        return redirect(url_for('show_status'))

@app.route('/build_schedule')
def build_schedule():
    global last_month
    last_month = (last_month + 1) % 2   
    if my_schedual == None:
        return redirect(url_for('home'))
    my_schedual.reload()
    my_schedual.bind_schedual()
    my_schedual.basic_schedual(last_month=last_month)
    return render_template("show_schedule.html", month=month, days=format.week_day_of_month(), \
                           employees=my_schedual.get_employee_json(use_state=True), \
                            departments=my_schedual.get_department_json(use_state=True), \
                                title=f"{year}年 {month}月 班表")

@app.route('/to_excel')
def to_excel():
    global year, month
    df = my_schedual.to_excel(month)
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=True)
    output.seek(0)

    # 使用 send_file 返回文件
    return send_file(output, as_attachment=True, download_name=f"{year}年{month}月班表.xlsx", \
                     mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')

@app.route('/save_reusable_data', methods=['GET', 'POST'])
def save_reusable_data():
    if request.method == 'GET':
        return render_template('save_reusable_data.html')
    else:
        if my_schedual == None:
            return redirect(url_for('home'))
        my_schedual.save_reuseable_data(f"{SAVE_PATH}/{request.form["file_name"]}.json")

        return redirect(url_for('show_status'))


def web_open():
    webbrowser.open_new('http://127.0.0.1:5000/')

if __name__ == '__main__':
    threading.Timer(1.25, web_open).start()
    app.run(debug=False)
    