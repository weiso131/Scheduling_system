import numpy as np
import copy
class schedual_format():
    def __init__(self, day_nums : int, period : int, start_day : int, period_name=[]):
        """
        day_nums : the number of days the schedule will be made

        period : the number of the periods in a day

        start_day : the start day of the schedule (1 for Monday, 0 for Sunday)

        period_name : an optional list of names for each period. If not provided, it will default to numbers from 1 to period.
        """
        self.day_nums = day_nums
        self.period = period
        self.start_day = start_day % 7
        self.period_name = period_name
        if len(self.period_name) == 0:
            self.period_name = []
            for i in range(1, self.period + 1):
                self.period_name.append(str(i))

        self.manpower_in_days = np.ones((self.day_nums, self.period))

    
    def check_period(self, periods : list):
        for i in periods:
            if i > self.period:
                print("有不存在的時段，請重新確認輸入")
                return True
        return False
    
    def check_day(self, day : int):
        if day < 0 or day >= self.day_nums:
            print("有不存在的日期，請重新確認輸入")
            return True
        return False

    def set_manpower_in_week(self, week_day : int, manpower : int):
            
        for i in range((week_day - self.start_day + 7) % 7, self.day_nums, 7):
            for j in range(self.period):
                self.manpower_in_days[i][j] = manpower
    
    def set_manpower_day(self, day : int, manpower : int):
        if self.check_day(day):
            return
        for j in range(self.period):
            self.manpower_in_days[day][j] = manpower

class human():
    def __init__(self, name : str, format : schedual_format):
        self.name = name
        self.format = copy.deepcopy(format)
        self.state = []

        for i in range(self.format.day_nums):
            self.state.append([])
            for j in range(self.format.period):
                if (self.format.manpower_in_days[i][j] == 0):  
                    self.state[i].append(["X"])
                else:
                    self.state[i].append([" "])
    def set_rest(self, day : int, periods : list):
        """
        set the period don't need any manpower
        """
        if self.format.check_period(periods) or self.format.check_day(day):
            return
        
        for j in periods:
            self.format.manpower_in_days[day][j] = 0
            self.state[day][j] = ["X"]
    

class department(human):
    def __init__(self, name : str, format : schedual_format):
        super().__init__(name, format)
    
    def change_manpower(self, day : int, periods : list, manpower : int):
        """"
        change the need of the manpower on the periods
        """
        if self.format.check_period(periods) or self.format.check_day(day):
            return
        
        for j in periods:
            self.format.manpower_in_days[day][j] = manpower
            while len(self.state[day][j]) < int(self.format.manpower_in_days[day][j]): 
                self.state[day][j].append(" ")
            while len(self.state[day][j]) > int(self.format.manpower_in_days[day][j]): 
                self.state[day][j].pop()
    def set_rest_week(self, week_day : int, periods : list):
        for i in range((week_day - self.format.start_day + 7) % 7, self.format.day_nums, 7):
            self.set_rest(i, periods)
    
class employee(human):

    def __init__(self, name : str, format : schedual_format, hate_departments=[]):
        super().__init__(name, format)
        self.hate_departments = hate_departments
    

class schedual():

    def __init__(self, departments : list, employees : list, format : schedual_format):
        self.departments = departments
        self.employees = employees
        self.format = format

    def schedual_fill(self, department_index : int, employee_index : int, day : int, period : int):
        man_fill_pos = len(self.departments[department_index].state[day][period]) - \
            int(self.departments[department_index].format.manpower_in_days[day][period])

        self.departments[department_index].state[day][period][man_fill_pos] = self.employees[employee_index].name
        self.employees[employee_index].state[day][period] = [self.departments[department_index].name]

        self.departments[department_index].format.manpower_in_days[day][period] -= 1
        self.employees[employee_index].format.manpower_in_days[day][period] -= 1

    def basic_schedual(self):
        for i in range(len(self.employees)):
            
            department_index = i % len(self.departments)

            for day in range(self.format.day_nums):
                if (day + self.format.start_day) % 14 == 0:
                    department_index = (department_index + 1) % len(self.departments)

                
                for period in range(self.format.period):
                    if self.departments[department_index].format.manpower_in_days[day][period] > 0 and \
                        self.employees[i].format.manpower_in_days[day][period] > 0:
                            self.schedual_fill(department_index, i, day, period)

                


                
                





