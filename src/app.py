from flask import Flask, request, jsonify, redirect, url_for, render_template
from scheduling import *

DEPARTMNT = 0
EMPLOYEE = 1

month = 7

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

@app.route('/show_status')
def show_status():
    return render_template('home.html', employees=my_schedual.get_employee_json(), \
                           departments=my_schedual.get_department_json(), target_class=EMPLOYEE)


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
    if request.method == 'GET':
        return render_template('employee_form.html')
    else:
        name = request.form['name']
        last_room = request.form['last_working_room']
        my_schedual.employees.append(Employee(name, last_room, format))
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
    return render_template("show_schedule.html", month=month, days=list(range(1, format.day_nums + 1)), employees=my_schedual.get_employee_json(use_state=True))
    

if __name__ == '__main__':
    app.run(debug=True)