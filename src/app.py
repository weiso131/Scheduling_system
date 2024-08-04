from datetime import datetime, date
import calendar

from flask import Flask, request, redirect, url_for, render_template


from scheduling import *
from tool import *

DEPARTMNT = 0
EMPLOYEE = 1

year = -1
month = 7
last_month = 0 #是否接續上個月

format = None
my_schedual = None

app = Flask(__name__)


def set_employee_data(form : dict):
    name = form['name']
    last_room = form['last_working_room']
    hate_periods = get_period(form['hate_period'])
    bind_periods = get_period(form['bind_period'])
    personal_leave = get_personal_leave(form['personal_leave'])

    
    new_employee = Employee(name, last_room, format, bind_period=bind_periods, \
                            hate_period=hate_periods, personal_leave=personal_leave)
        
    return new_employee

@app.route('/', methods=['GET', 'POST'])
def home():
    global year, month, format, my_schedual
    if request.method == 'GET':
        now = datetime.now()
        return render_template('home.html', default_data={"year" : str(now.year), "month" : str(now.month)})
    else:
        year = int(request.form['year'])
        month = int(request.form['month'])

        specific_day = date(year, month, 1)
        start_day = (specific_day.weekday() + 1 ) % 7
        day_nums = calendar.monthrange(year, month)[1]
        
        format = SchedualFormat(day_nums=day_nums, period=2, start_day=start_day, period_name=["上午", "下午"])
        format.set_manpower_in_week(week_day=6, manpower=0, period=[1])
        format.set_manpower_in_week(week_day=7, manpower=0, period=[0, 1])

        my_schedual = ScheduleContainer(format)
        my_schedual.departments = [Department("82", format), Department("83", format), Department("84", format)]
        my_schedual.employees = [Employee("A", "82", format), Employee("B", "83", format), Employee("C", "84", format)]

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
                                   post_url=url_for('edit', target_class=target_class, id=id))
        else:
            my_schedual.employees[id] = set_employee_data(request.form)
            return redirect(url_for('show_status')) 

    else:
        pass


    return "meow"

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
                               post_url=url_for('add_employee'))
    else:
        new_employee = set_employee_data(request.form)
        my_schedual.employees.append(new_employee)

        return redirect(url_for('show_status'))



@app.route('/add_department', methods=['GET', 'POST'])
def add_department():
    if my_schedual == None:
        return redirect(url_for('home'))
    
    if request.method == 'GET':
        return render_template('department_form.html')
    else:
        name = request.form['name']
        my_schedual.departments.append(Department(name, format))
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
                           employees=my_schedual.get_employee_json(use_state=True), title=f"{year}年 {month}月 班表")

@app.route('/to_excel')
def to_excel():
    return "meow"

if __name__ == '__main__':
    app.run(debug=True)