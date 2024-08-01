import copy


from .SchedualFormat import *

class Human():
    def __init__(self, name : str, format : SchedualFormat):
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
                    self.state[i].append(["_"])
        
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
    def __init__(self, name : str, format : SchedualFormat):
        super().__init__(name, format)
    def change_manpower(self, day : int, periods : list, manpower : int):
        """"
        change the need of the manpower on the periods
        """
        if self.format.check_period(periods) or self.format.check_day(day):
            return
        for j in periods:
            self.basic_format[day][j] = manpower
            self.format.manpower_in_days[day][j] = manpower
            while len(self.state[day][j]) < int(self.format.manpower_in_days[day][j]): 
                self.state[day][j].append(" ")
            while len(self.state[day][j]) > int(self.format.manpower_in_days[day][j]): 
                self.state[day][j].pop()
    def set_rest_week(self, week_day : int, periods : list):
        for i in range((week_day - self.format.start_day + 7) % 7, self.format.day_nums, 7):
            self.set_rest(i, periods)
    def schedual_fill(self, fill_name : str, day : int, period : int):
        man_fill_pos = len(self.state[day][period]) - int(self.format.manpower_in_days[day][period])
        self.state[day][period][man_fill_pos] = fill_name
        self.format.manpower_in_days[day][period] -= 1
    
class Employee(Human):
    def __init__(self, name : str, start_department : str, format : SchedualFormat, hate_period=[], bind_period=[]):
        """
        hate_period : [("department_name", day, [periods, ])]
        bind_period : [("department_name", day, [periods, ])]
        """
        super().__init__(name, format)
        self.start_department = start_department
        self.hate_period = hate_period
        self.bind_period = bind_period
    def schedual_one_day_output(self, day : int):
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
                (day + self.format.start_day) % 7 == hate_day and period in hate_periods 
                             
            employee_avalible = employee_avalible and (not is_hate_period)
        return employee_avalible
    def schedual_fill(self, fill_name : str, day : int, period : int):
        self.state[day][period][0] = fill_name
        self.format.manpower_in_days[day][period] -= 1
