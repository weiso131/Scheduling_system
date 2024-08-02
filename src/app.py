from datetime import datetime, date
import calendar

from flask import Flask, request, redirect, url_for, render_template


from scheduling import *
from tool import *

DEPARTMNT = 0
EMPLOYEE = 1

year = -1
month = 7
start_day = 1
day_nums = 31

format = SchedualFormat(day_nums=day_nums, period=2, start_day=start_day)
format.set_manpower_in_week(week_day=6, manpower=0, period=[1])
format.set_manpower_in_week(week_day=7, manpower=0, period=[0, 1])

my_schedual = ScheduleContainer(format)
my_schedual.departments = [Department("82", format), Department("83", format)]
my_schedual.employees = [Employee("teddy", "82", format), Employee("weiso", "83", format)]

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def home():
    global year, month, start_day, day_nums
    if request.method == 'GET':
        now = datetime.now()
        return render_template('home.html', \
                               default_data={"year" : str(now.year), "month" : str(now.month)})
    else:
        year = int(request.form['year'])
        month = int(request.form['month'])

        specific_day = date(year, month, 1)
        start_day = (specific_day.weekday() + 1 ) % 7
        day_nums = calendar.monthrange(year, month)[1]
        
        return redirect(url_for('show_status'))

@app.route('/show_status')
def show_status():
    global month
    return render_template('show_status.html', employees=my_schedual.get_employee_json(), \
                           departments=my_schedual.get_department_json(), target_class=EMPLOYEE, 
                           title=f"{year}年 {month}月 班表")


@app.route('/edit/<int:target_class>/<int:id>')
def edit(target_class, id):
    return "meow"

@app.route('/delete/<int:target_class>/<int:id>')
def delete(target_class, id):
    if target_class == EMPLOYEE:
        my_schedual.employees.pop(id)
        return redirect(url_for('show_status'))
    else:
        my_schedual.departments.pop(id)
        return redirect(url_for('show_status'))
    
@app.route('/add_employee', methods=['GET', 'POST'])
def add_employee():
    global year, month, day_nums
    if request.method == 'GET':
        return render_template('employee_form.html', year=year, month=month, dates=list(range(1, day_nums + 1)))
    else:
        name = request.form['name']
        last_room = request.form['last_working_room']
        hate_periods = get_period(request.form['hate_period'])
        bind_periods = get_period(request.form['bind_period'])
        personal_leave = get_personal_leave(request.form['personal_leave'])

        if type(hate_periods) is str or type(bind_periods) is str or type(personal_leave) is str:
            return render_template('employee_form.html', year=year, month=month, dates=list(range(1, day_nums + 1)))
        
        new_employee = Employee(name, last_room, format, bind_period=bind_periods, hate_period=hate_periods)
        for pl in personal_leave:
            new_employee.set_rest_period(pl)
        my_schedual.employees.append(new_employee)

        return redirect(url_for('show_status'))



@app.route('/add_department', methods=['GET', 'POST'])
def add_department():
    if request.method == 'GET':
        return render_template('department_form.html')
    else:
        name = request.form['name']
        my_schedual.departments.append(Department(name, format))
        return redirect(url_for('show_status'))

@app.route('/build_schedule')
def build_schedule():
    my_schedual.reload()
    my_schedual.bind_schedual()
    my_schedual.basic_schedual(last_month=1)
    return render_template("show_schedule.html", month=month, days=list(range(1, format.day_nums + 1)), \
                           employees=my_schedual.get_employee_json(use_state=True), title=f"{year}年 {month}月 班表")
    

if __name__ == '__main__':
    app.run(debug=True)