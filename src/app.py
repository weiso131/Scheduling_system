from flask import Flask, request, jsonify, redirect, url_for, render_template
from scheduling import *

DEPARTMNT = 0
EMPLOYEE = 1


format = SchedualFormat(day_nums=31, period=2, start_day=1)
format.set_manpower_in_week(week_day=6, manpower=0, period=[1])
format.set_manpower_in_week(week_day=7, manpower=0, period=[0, 1])

my_schedual = ScheduleContainer(format)
my_schedual.departments = [Department("82", format), Department("83", format)]
my_schedual.employees = [Employee("teddy", "82", format), Employee("weiso", "83", format)]

app = Flask(__name__)

@app.route('/')
def home():
    return redirect(url_for('show_employees_status'))

@app.route('/employees')
def show_employees_status():
    return render_template('home.html', data=my_schedual.get_employee_json(), target_class=EMPLOYEE)

@app.route('/departments')
def show_departments_status():
    return render_template('home.html', data=my_schedual.get_department_json(), target_class=DEPARTMNT)

@app.route('/edit/<int:target_class>/<int:id>')
def edit(target_class, id):
    return "meow"

@app.route('/delete/<int:target_class>/<int:id>')
def delete(target_class, id):
    if target_class == EMPLOYEE:
        my_schedual.employees.pop(id)
        return redirect(url_for('show_employees_status'))
    else:
        my_schedual.departments.pop(id)
        return redirect(url_for('show_departments_status'))
    

if __name__ == '__main__':
    app.run(debug=True)