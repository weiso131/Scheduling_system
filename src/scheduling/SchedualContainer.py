import pandas as pd

from .Human import *

class ScheduleContainer():
    def __init__(self, format : SchedualFormat, departments=[], employees=[]):
        self.departments = departments
        self.employees = employees
        self.format = format
    def check_avalible(self, department_index : int, employee_index : int, day : int, period : int):
        department_need = self.departments[department_index].check_avaliable(day, period)
        employee_avalible = self.employees[employee_index].check_avaliable(day, period, self.departments[department_index])
        return department_need and employee_avalible
    def schedual_fill(self, department_index : int, employee_index : int, day : int, period : int):
        
        self.departments[department_index].schedual_fill(self.employees[employee_index].name, day, period)
        self.employees[employee_index].schedual_fill(self.departments[department_index].name, day, period)
    def get_department_index(self, department_name : str):
        for i in range(len(self.departments)):
            if self.departments[i].name == department_name:
                return i
        return -1
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
    def bind_schedual(self):
        for i in range(len(self.employees)):
            if len(self.employees[i].bind_period) == 0:
                continue
            
            for bind_name, bind_day, bind_period in self.employees[i].bind_period:
                department_index = self.get_department_index(bind_name)
                
                
                for day in range((bind_day - self.format.start_day + 7) % 7, self.format.day_nums, 7):
                    e_avalible = self.check_avalible(department_index, i, day, bind_period)
                    if e_avalible and department_index != -1:
                        self.schedual_fill(department_index, i, day, bind_period)
                    #consider employee will go to the department not need to arrange schedule
                    elif e_avalible and department_index == -1:
                        self.employees[i].schedual_fill(bind_name, day, bind_period)
    def basic_schedual(self, last_month=0):
        for i in range(len(self.employees)):
            
            department_index = self.get_department_index(self.employees[i].start_department)

            for day in range(self.format.day_nums):
                if (day + self.format.start_day + last_month * 7) % 14 == 0:
                    department_index = (department_index + 1) % len(self.departments)

                
                for period in range(self.format.period):
                    if self.check_avalible(department_index, i, day, period):
                            self.schedual_fill(department_index, i, day, period)
    def to_excel(self):
        week_day_chinese = ["日", "一", "二", "三", "四", "五", "六"]
        data = {}
        for day in range(self.format.day_nums):
            data[str(day + 1)] = [week_day_chinese[(day + self.format.start_day + 7) % 7]]
            for e in self.employees:
                data[str(day + 1)].append(e.schedual_one_day_output(day))
        df = pd.DataFrame(data)
        custom_index = ["星期"]
        for e in self.employees:
            custom_index.append(e.name)
        df.index = custom_index
        df.to_excel("schedual.xlsx", index=True)
