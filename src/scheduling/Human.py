import copy

from .tool import get_token
from .ScheduleFormat import ScheduleFormat



class Human():
    def __init__(self, name : str, format : ScheduleFormat):
        self.name = name
        self.basic_format = copy.deepcopy(format)
        self.reload()
        
    def reload(self):
        """
        重新整理self.format 和 self.state的狀態
        """
        self.format = copy.deepcopy(self.basic_format)
        self.state = []
        for i in range(self.format.day_nums):
            self.state.append([])
            for j in range(self.format.period):
                if self.format.manpower_in_days[i][j] == 0:
                    self.state[i].append(["X"])
                else:
                    self.state[i].append([])
                    for _ in range(int(self.format.manpower_in_days[i][j])):
                        self.state[i][j].append("_")
        
    def set_rest(self, day : int, periods : list):
        """
        將某個部門/員工的某個時段設成休假
        """
        if self.format.check_period(periods) or self.format.check_day(day):
            return        
        for j in periods:
            self.basic_format.manpower_in_days[day][j] = 0
            self.format.manpower_in_days[day][j] = 0
            self.state[day][j] = ["X"]
    def print_state(self):
        for i in range(self.format.day_nums):
            print(i + 1, self.state[i], end="/ /")
            if (i + self.format.start_day) % 7 == 0:
                print()
        print()
    def check_avaliable(self, day : int, period : int):
        return self.format.manpower_in_days[day][period] > 0

class Department(Human):
    def __init__(self, name : str, format : ScheduleFormat, man_power_input="", rest_time_input=""):
        super().__init__(name, format)
        self.man_power = get_token(man_power_input, "w/p/n")
        self.rest_time = get_token(rest_time_input, "w/p")
        self.man_power_input = man_power_input
        self.rest_time_input = rest_time_input


        for week_day, period, man_power in self.man_power:
            self.change_manpower_week(week_day, period, man_power)
        for week_day, period in self.rest_time:
            self.set_rest_week(week_day, period)
    def change_manpower(self, day : int, period : int, manpower : int):
        """"
        change the need of the manpower on the periods
        """
        if self.format.check_period([period]) or self.format.check_day(day):
            return

        self.basic_format.manpower_in_days[day][period] = manpower
        self.format.manpower_in_days[day][period] = manpower
        while len(self.state[day][period]) < int(self.format.manpower_in_days[day][period]): 
            self.state[day][period].append("_")
        while len(self.state[day][period]) > int(self.format.manpower_in_days[day][period]): 
            self.state[day][period].pop()
        
    def change_manpower_week(self, week_day : int, period : int, manpower : int):
        for i in range((week_day - self.format.start_day + 7) % 7, self.format.day_nums, 7):
            self.change_manpower(i, period, manpower)
    def set_rest_week(self, week_day : int, period : int):
        for i in range((week_day - self.format.start_day + 7) % 7, self.format.day_nums, 7):
            self.set_rest(i, [period])
    def schedule_fill(self, fill_name : str, day : int, period : int):
        man_fill_pos = len(self.state[day][period]) - int(self.format.manpower_in_days[day][period])
        self.state[day][period][man_fill_pos] = fill_name
        self.format.manpower_in_days[day][period] -= 1

    def get_remark(self):
        output = {"man_power" : "", "rest_time" : ""}
        if self.man_power_input != "":
            output["man_power"] = "人力更動:" + self.man_power_input
        if self.rest_time_input!= "":
            output["rest_time"] = "休診時間:" + self.rest_time_input

        return output
    
class Employee(Human):
    def __init__(self, name : str, start_department : str, format : ScheduleFormat, hate_period_input="", \
                 bind_period_input="", personal_leave_input=""):
        """
        hate_period : [("department_name", day, [periods, ])]
        bind_period : [("department_name", day, [periods, ])]
        """
        super().__init__(name, format)
        self.start_department = start_department
        self.hate_period = get_token(hate_period_input, 's/w/p')
        self.bind_period = get_token(bind_period_input, 's/w/p')
        self.personal_leave = get_token(personal_leave_input, 'd/p')

        self.hate_period_input = hate_period_input
        self.bind_period_input = bind_period_input
        self.personal_leave_input = personal_leave_input

        for pl in self.personal_leave:
            self.set_rest(pl[0], [pl[1]])
        
    def schedule_one_day_output(self, day : int):
        employee_work = ""
        for p in range(self.format.period):
            employee_work += self.state[day][p][0]
            if p != self.format.period - 1:
                employee_work += " "
        return employee_work
    def check_avaliable(self, day: int, period: int, department : Department):
        employee_avalible = super().check_avaliable(day, period)
        
        for hate_name, hate_day, hate_periods in self.hate_period:
            
            is_hate_period = hate_name == department.name and\
                (day + self.format.start_day) % 7 == hate_day and period == hate_periods 
                             
            employee_avalible = employee_avalible and (not is_hate_period)
        return employee_avalible
    def schedule_fill(self, fill_name : str, day : int, period : int):
        self.state[day][period][0] = fill_name
        self.format.manpower_in_days[day][period] -= 1
    def get_remark(self):
        week = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat']

        output = {"personal_leave" : '', "hate_period" : '', "bind_period" : ''}
        
        if len(self.personal_leave_input) != 0:
            output['personal_leave'] = "請假:" + self.personal_leave_input
        if len(self.hate_period_input) != 0:
            output['hate_period'] = "不想跟的診間時段:" + self.hate_period_input
        if len(self.bind_period_input) != 0:
            output['bind_period'] = "被指定的診間時段:" + self.bind_period_input

        return output

        
    
                    



