from dataclasses import dataclass, field
import time, calendar, datetime, ephem, itertools

class Event():
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
        'ms' - depends on moon state:
            0 - New Moon,
            1 - Perfect Waxing Crescent,
            2 - 1st Quarter,
            3 - Perfect Waxing Gibbous,
            4 - Full Moon
            5 - Perfect Waning Gibbous,
            6 - 3rd Quarter,
            7 - Perfect Waning Crescent
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
            return [i for i in itertools.takewhile(lambda x: x <= maximum_days, range(1, int(time.strftime('%d', time.gmtime(time.time() + (3600 * self.settings.utf_difference)))) + a + 1)) if 1 <= i] # https://stackoverflow.com/questions/9572833/using-break-in-a-list-comprehension
        elif self.mode == "ms":
            if type(args) is not dict:
                raise Exception("Argument must be dict")
            for i in args:
                if type(i) is not int or i > 7 or i < 0:
                    raise Exception("Keys for arguments must be an integer and must be between 0 and 7, inclusive")
            return self.lunar_mode(args)
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

    def lunar_midpoint(self, start_point: ephem.Date.datetime, end_point: ephem.Date.datetime):
        date_difference = int((end_point - start_point).total_seconds())
        return ephem.Date(datetime.datetime.fromtimestamp(start_point.timestamp() + (date_difference >> 1))).datetime()

    def correct_time_zone(self, date_time, UTF_difference):
        return datetime.datetime.fromtimestamp(date_time.timestamp() + (3600 * UTF_difference))

    def get_moon_dates(self):
        year, month, utf_difference = self.settings.year, self.settings.month, self.settings.utf_difference

        start = ephem.Date(datetime.date(year - 1, 12, 1)) if month == 1 else ephem.Date(datetime.date(year, month - 1, 1))
        end = ephem.Date(datetime.date(year + 1, 1, 1)) if month == 12 else ephem.Date(datetime.date(year, month + 1, 1))

        moon_dates = {"New Moon": [], "Perfect Waxing Crescent": [], "1st Quarter": [], "Perfect Waxing Gibbous": [], "Full Moon": [], "Perfect Waning Gibbous": [], "3rd Quarter": [], "Perfect Waning Crescent": []}

        date = start
        full_moon_date = date # cycle starts and ends in full moon
        while date < end:
            # new moon
            new_moon_date = ephem.next_new_moon(date)

            # full moon
            full_moon_date = ephem.next_full_moon(date)

            if full_moon_date > new_moon_date:
                new_moon_datetime = self.correct_time_zone(new_moon_date.datetime(), utf_difference)
                full_moon_datetime = self.correct_time_zone(full_moon_date.datetime(), utf_difference)

                if new_moon_datetime.year == year and new_moon_datetime.month == month:
                    moon_dates["New Moon"].append(new_moon_datetime.day)

                # 1st Quarter
                first_quarter_datetime = self.lunar_midpoint(new_moon_datetime, full_moon_datetime)
                if first_quarter_datetime.year == year and first_quarter_datetime.month == month:
                    moon_dates["1st Quarter"].append(first_quarter_datetime.day)

                # Waxing Cresent
                waxing_crescent_datetime = self.lunar_midpoint(new_moon_datetime, first_quarter_datetime)
                if waxing_crescent_datetime.year == year and waxing_crescent_datetime.month == month:
                    moon_dates["Perfect Waxing Crescent"].append(waxing_crescent_datetime.day)

                # Waxing Gibbous
                waxing_gibbous_datetime = self.lunar_midpoint(first_quarter_datetime, full_moon_datetime)
                if waxing_gibbous_datetime.year == year and waxing_gibbous_datetime.month == month:
                    moon_dates["Perfect Waxing Gibbous"].append(waxing_gibbous_datetime.day)

                date = ephem.Date(datetime.date(full_moon_datetime.year, full_moon_datetime.month, full_moon_datetime.day - 1))

            elif full_moon_date < new_moon_date:
                new_moon_datetime = self.correct_time_zone(new_moon_date.datetime(), utf_difference)
                full_moon_datetime = self.correct_time_zone(full_moon_date.datetime(), utf_difference)

                if full_moon_datetime.year == year and full_moon_datetime.month == month:
                    moon_dates["Full Moon"].append(full_moon_datetime.day)

                # 3rd Quarter
                third_quarter_datetime = self.lunar_midpoint(full_moon_datetime, new_moon_datetime)
                if third_quarter_datetime.year == year and third_quarter_datetime.month == month:
                    moon_dates["3rd Quarter"].append(third_quarter_datetime.day)

                # Waning Gibbous
                waning_gibbous_datetime = self.lunar_midpoint(full_moon_datetime, third_quarter_datetime)
                if waning_gibbous_datetime.year == year and waning_gibbous_datetime.month == month:
                    moon_dates["Perfect Waning Gibbous"].append(waning_gibbous_datetime.day)

                # Waning Crescent
                waning_crescent_datetime = self.lunar_midpoint(third_quarter_datetime, new_moon_datetime)
                if waning_crescent_datetime.year == year and waning_crescent_datetime.month == month:
                    moon_dates["Perfect Waning Crescent"].append(waning_crescent_datetime.day)

                date = ephem.Date(datetime.date(new_moon_datetime.year, new_moon_datetime.month, new_moon_datetime.day - 1))

        return moon_dates

    def lunar_mode(self, lunar_choices: dict):
        year, month = self.settings.year, self.settings.month

        convert_table = {
            0: "New Moon",
            1: "Perfect Waxing Crescent",
            2: "1st Quarter",
            3: "Perfect Waxing Gibbous",
            4: "Full Moon",
            5: "Perfect Waning Gibbous",
            6: "3rd Quarter",
            7: "Perfect Waning Crescent"
        }
        supported = []
        for choice in lunar_choices:
            choice_name = convert_table[choice]
            lunar_days = self.get_moon_dates()[choice_name]
            for day in lunar_days:
                for increment in lunar_choices[choice]:
                    new_year, new_month, new_day = Event.add_increment(datetime.datetime(year, month, day), increment, self.settings)
                    if new_year == year and new_month == month:
                        supported += [new_day]
        return supported

    @staticmethod
    def add_increment(date, increment, settings):
        year, month, day = date.year, date.month, date.day
        day += increment

        num_days = Event.number_days(settings)
        while day > num_days:
            day -= num_days
            month += 1

            if month > 12:
                month = 1
                year += 1

            num_days = Event.number_days(settings)

        return year, month, day

    @staticmethod
    def number_days(settings):
        return calendar.monthrange(settings.year, settings.month)[1]

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







