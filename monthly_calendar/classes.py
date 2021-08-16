from dataclasses import dataclass, field
import time, calendar, itertools

class Event():
    # NOT YET SUPPORTED
    # 'ms' - depends on moon state:
    #     0 - New Moon,
    #     1 - Waxing Crescent,
    #     2 - 1st Quarter,
    #     3 - Waxing Gibbous,
    #     4 - Full Moon
    #     5 - Waning Gibbous,
    #     6 - 3rd Quarter,
    #     7 - Waning Crescent
    def __init__(self, typing, mode, settings, args = None, custom = None):
        '''
        All typing is the images you placed on the resources.

        All modes:
        'd' - by day, enter all days that this applies via args
        'td' - depending on day of the week, example every Sunday, input 6 to include "Sunday" which then apply to the entire column
        'wd' - applies to weekdays in the whole month
        'we' - applies to weekends in the whole month
        'u' - updated, from start of month to today, this typing will be applied (this only works if the month and year is default, meaning, this month and this year)
            You can add positive or negative number to indicate how far ahead or behind today.
        '''
        if args is None:
            args = []

        self.typing = typing
        self.mode = mode
        self.settings = settings
        self.applies_to = self.check_arguments(args)
        self.custom = custom
        if typing == "labeled":
            self.custom = str(custom)
        elif typing == "block":
            self.custom = list(custom)

    def check_arguments(self, args):
        maximum_days = Event.number_days(self.settings)
        if self.mode == "d":
            for i in args:
                if type(i) != int or 1 > i or i > maximum_days:
                    raise Exception("Wrong datatype. 'd' mode takes integers from 1 to end of month or it may be that it is out of the range of possible days")
            return list(args)
        elif self.mode == "td":
            return self.column_mode(args)
        elif self.mode == "wd":
            return self.column_mode((0, 1, 2, 3, 4))
        elif self.mode == "we":
            return self.column_mode((5, 6))
        elif self.mode == "u":
            if len(args) > 1:
                raise Exception("You can only have one or zero additional argument for update mode")
            elif len(args) == 1:
                a, = args
                if type(a) != int:
                    raise Exception("Int is required for updated mode")
            else:
                a = 0
            return [i for i in itertools.takewhile(lambda x: x <= maximum_days, range(1, int(time.strftime('%d', time.localtime(time.time()))) + a + 1)) if 1 <= i] # https://stackoverflow.com/questions/9572833/using-break-in-a-list-comprehension
        else:
            raise Exception(f"mode '{self.mode}' is not supported")

    def column_mode(self, day_index):
        names = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        supported = []
        for i in day_index:
            if type(i) != int:
                raise Exception("Wrong datatype. column modes, like 'td', 'wd', and 'we' accepts integers only 0 = Monday ... 6 = Sunday")
            i %= 7
            day = names[i]

            month_days = calendar.Calendar(self.settings.day_start).monthdayscalendar(self.settings.year, self.settings.month)
            for a, week in zip(range(len(month_days)), month_days):
                for b, number in zip(range(len(week)), week):
                    if number != 0:
                        identifier = self.settings.day_start + b
                        if Event.day_title(identifier) == day:
                            supported.append(number)
                            break
        return supported

    @staticmethod
    def number_days(settings):
        cal = calendar.Calendar(settings.day_start)
        month_days = cal.monthdayscalendar(settings.year, settings.month)

        number = 0
        for week in month_days:
            for day in week:
                if day != 0:
                    number += 1
        return number
        # leap = 0
        # if year % 4 == 0:
        #     leap = 1
        # if month == 2:
        #     return 28 + leap
        # elif month in [4, 6, 9, 11]:
        #     return 30
        # else:
        #     return 31
            
    @staticmethod
    def day_title(day, length = None):
        day %= 7
        day_name = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        return day_name[day][0:length]

@dataclass(order = True)
class Day_Type():
    sort_index: int = field(init = False, repr = False)
    name: str
    path: str
    order: int
    favorability: int
    mode_name: str

    def __repr__(self):
        return f"type.{self.mode_name}"

    def __post_init__(self):
        self.sort_index = self.order





# supported += [start + (7 * i) for i in range((maximum_days // 7) + 1)]
