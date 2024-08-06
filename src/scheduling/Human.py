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
    def __init__(self, name : str, format : SchedualFormat, man_power=[], rest_time=[], man_power_input="", rest_time_input=""):
        super().__init__(name, format)
        self.man_power = man_power
        self.rest_time = rest_time
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
    def schedual_fill(self, fill_name : str, day : int, period : int):
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
    def __init__(self, name : str, start_department : str, format : SchedualFormat, hate_period=[], bind_period=[], personal_leave=[]):
        """
        hate_period : [("department_name", day, [periods, ])]
        bind_period : [("department_name", day, [periods, ])]
        """
        super().__init__(name, format)
        self.start_department = start_department
        self.hate_period = hate_period
        self.bind_period = bind_period
        self.personal_leave = personal_leave

        self.hate_period_input = self.__get_period(hate_period)
        self.bind_period_input = self.__get_period(bind_period)
        self.personal_leave_input = self.__get_personal_leave()

        for pl in personal_leave:
            self.__set_rest_period(pl)
        
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
    def __set_rest_period(self, personal_leave : tuple):
        start_day, start_period, end_day, end_period = personal_leave
        for i in range(start_day, end_day + 1):

            start, end = 0, self.format.period

            if i == start_day:
                start = start_period
            elif i == end_day:
                end = end_period

            self.set_rest(i, list(range(start, end)))
    def get_remark(self):
        week = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat']

        output = {"personal_leave" : '', "hate_period" : '', "bind_period" : ''}
        
        if len(self.personal_leave_input) != 0:
            output['personal_leave'] = "請假:" + self.personal_leave_input
        if len(self.hate_period_input) != 0:
            output['hate_period'] = "不想跟的診間時段:" + self.__get_period(self.hate_period, week=week)
        if len(self.bind_period_input) != 0:
            output['bind_period'] = "被指定的診間時段:" + self.__get_period(self.bind_period, week=week)

        return output
    def __get_period(self, periods : list, week=list(range(0, 7))) -> str:
        output = ""
        for i in range(len(periods)):
            period = periods[i]
            output += f"{period[0]}/{week[period[1]]}/{self.format.period_name[period[2]]}"
            if i != len(periods) - 1:
                output += ","
        return output
    def __get_personal_leave(self):
        output = ""
        for i in range(len(self.personal_leave)):
            personal_leave = self.personal_leave[i]
            output += "{}/{}~{}/{}".format(personal_leave[0] + 1, self.format.period_name[personal_leave[1]],\
                                           personal_leave[2] + 1, self.format.period_name[personal_leave[3]])
            if i != len(self.personal_leave) - 1:
                output += ","
        return output
        
    
                    



