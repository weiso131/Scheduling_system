import pandas as pd
import json

from .Human import Employee, Department, ScheduleFormat

class ScheduleContainer():
    def __init__(self, format : ScheduleFormat, departments=[], employees=[]):
        self.departments = departments
        self.employees = employees
        self.format = format
    def __check_avalible(self, department_index : int, employee_index : int, day : int, period : int):
        department_need = self.departments[department_index].check_avaliable(day, period)
        employee_avalible = self.employees[employee_index].check_avaliable(day, period, self.departments[department_index])
        return department_need and employee_avalible
    def __schedule_fill(self, department_index : int, employee_index : int, day : int, period : int):
        
        self.departments[department_index].schedule_fill(self.employees[employee_index].name, day, period)
        self.employees[employee_index].schedule_fill(self.departments[department_index].name, day, period)
    def __get_department_index(self, department_name : str):
        for i in range(len(self.departments)):
            if self.departments[i].name == department_name:
                return i
        return -1
    def set_employee_data(self, form : dict):
        name = form['name']
        last_room = form['last_working_room']
        
        new_employee = Employee(name, last_room, self.format, bind_period_input=form['bind_period'], \
                                hate_period_input=form['hate_period'], personal_leave_input=form['personal_leave'])
            
        return new_employee


    def set_department_data(self, form : dict):
        name = form['name']

        new_department = Department(name, self.format, man_power_input=form['man_power'], \
                                    rest_time_input=form['rest_time'])
        return new_department
    def reload(self):
        for department in self.departments:
            department.reload()
        for employee in self.employees:
            employee.reload()
    def get_department_json(self, use_state=False):
        json = []
        for i in range(len(self.departments)):
            json.append({"name": self.departments[i].name, "remark" : self.departments[i].get_remark(),"id" : i})
            if use_state:
                json[i]["state"] = self.departments[i].state
        return json
    def get_employee_json(self, use_state=False):
        json = []
        for i in range(len(self.employees)):
            json.append({"name": self.employees[i].name, "id" : i, \
                         "remark" : self.employees[i].get_remark(), \
                         "last_room" : self.employees[i].start_department})
            if use_state:
                json[i]["state"] = self.employees[i].state
        return json
    def save_reuseable_data(self, path : str):
        data = {"departments" : [], "employees" : []}
        for department in self.departments:
            data["departments"].append({"name" : department.name, \
                                        "man_power" : department.man_power_input, \
                                             "rest_time" : department.rest_time_input})
        for employee in self.employees:
            data["employees"].append({"name" : employee.name, \
                                             "last_working_room" : employee.start_department, \
                                             "hate_period" : employee.hate_period_input, \
                                                 "bind_period" : employee.bind_period_input, \
                                                    "personal_leave" : ""})

        with open(path, 'w', encoding="utf-8") as file:
            json.dump(data, file, ensure_ascii=False, indent=4)
    def load_reusable_data(self, path : str):
        with open(path, 'r', encoding="utf-8") as file:
            data = json.load(file)
        for employee in data["employees"]:
            new_employee = self.set_employee_data(employee)
            self.employees.append(new_employee)
        for department in data["departments"]:
            new_department = self.set_department_data(department)
            self.departments.append(new_department)


    def bind_schedule(self):
        for i in range(len(self.employees)):
            if len(self.employees[i].bind_period) == 0:
                continue
            
            for bind_name, bind_day, bind_period in self.employees[i].bind_period:
                department_index = self.__get_department_index(bind_name)
                
                
                for day in range((bind_day - self.format.start_day + 7) % 7, self.format.day_nums, 7):
                    e_avalible = self.__check_avalible(department_index, i, day, bind_period)
                    if e_avalible and department_index != -1:
                        self.__schedule_fill(department_index, i, day, bind_period)
                    #consider employee will go to the department not need to arrange schedule
                    elif e_avalible and department_index == -1:
                        self.employees[i].schedule_fill(bind_name, day, bind_period)
    def basic_schedule(self, last_month=0):
        for i in range(len(self.employees)):
            
            department_index = self.__get_department_index(self.employees[i].start_department)

            for day in range(self.format.day_nums):
                if (day + self.format.start_day + last_month * 7) % 14 == 0:
                    department_index = (department_index + 1) % len(self.departments)

                
                for period in range(self.format.period):
                    if self.__check_avalible(department_index, i, day, period):
                            self.__schedule_fill(department_index, i, day, period)
    def to_excel(self, month):
        week_day_chinese = ["(日)", "(一)", "(二)", "(三)", "(四)", "(五)", "(六)"]
        data = {}
        for day in range(self.format.day_nums):
            data[f"{month}/{day + 1}"] = [week_day_chinese[(day + self.format.start_day + 7) % 7]]
            for e in self.employees:
                data[f"{month}/{day + 1}"].append(e.schedule_one_day_output(day))
        
        custom_index = ["星期"]
        for e in self.employees:
            custom_index.append(e.name)

        df = pd.DataFrame(data)
        df.index = custom_index
        return df
