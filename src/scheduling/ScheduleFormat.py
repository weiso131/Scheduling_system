

import numpy as np



class ScheduleFormat():
    def __init__(self, day_nums : int, period : int, start_day : int, period_name=[]):
        """
        day_nums : the number of days the schedule will be made

        period : the number of the periods in a day

        start_day : the start day of the schedule (1 for Monday, 0 for Sunday)

        period_name : an optional list of names for each period. 
                    If not provided, it will default to numbers from 1 to period.
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
    def set_manpower_in_week(self, week_day : int, manpower : int, period : list):
        for i in range((week_day - self.start_day + 7) % 7, self.day_nums, 7):
            for j in period:
                self.manpower_in_days[i][j] = manpower
    def set_manpower_day(self, day : int, manpower : int):
        if self.check_day(day):
            return
        for j in range(self.period):
            self.manpower_in_days[day][j] = manpower
    def week_day_of_month(self):
        week = ['(日)', '(一)', '(二)', '(三)', '(四)', '(五)', '(六)']
        output = []
        for i in range(self.day_nums):
            output.append(f"{str(i + 1)} {week[(i + self.start_day + 7) % 7]}")
        
        return output

