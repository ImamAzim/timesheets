import os
import json
import datetime
import calendar


import pandas
import xdg
import numpy


def main():
    test()


def test():
    timesheet = TimeSheet()
    # timesheet.load('test', 2023)
    timesheet.create_new(2023, [])
    # timesheet.save('test')
    l = timesheet.get_holiday_rows()
    print(l)


APP_NAME = 'timesheets'

def date_iter(year, month):
    for i in range(1, calendar.monthrange(year, month)[1] + 1):
        yield datetime.date(year, month, i)

class TimeSheet(object):

    """Docstring for TimeSheet. """
    FULL_DAY_WORKTIME = datetime.timedelta(hours=8)

    def __init__(self):
        """TODO: to be defined.


        """
        self._df = None
        self._year = None
        directory = os.path.join(xdg.xdg_data_home(), APP_NAME)
        if not os.path.exists(directory):
            os.makedirs(directory)
        self.directory = directory

    @property
    def df(self):
        return self._df

    @df.setter
    def df(self, new_df):
        self._df = new_df

    def __repr__(self):
        text = self._df.to_string()
        return text

    def create_new(self, year, holidays):
        """create a new dataframe

        :year: int
        :holidays: list of date

        """
        self._year = year
        data = dict(month=[], day=[], weekday=[], AM_start=[], AM_end=[], PM_start=[], PM_end=[],workday=[], worktime=[], day_balance=[])

        for month in range(1, 13):
            for date in date_iter(year, month):
                data['month'].append(calendar.month_name[month])
                data['day'].append(date.day)
                data['weekday'].append(calendar.day_name[date.weekday()])
                time = datetime.time().isoformat(timespec='minutes')
                data['AM_start'].append(time)
                data['AM_end'].append(time)
                data['PM_start'].append(time)
                data['PM_end'].append(time)
                if date.weekday() > 4:
                    workday = False
                else:
                    workday = True
                data['workday'].append(workday)
                delta = str(datetime.timedelta())
                data['worktime'].append(delta)
                data['day_balance'].append(delta)

        df = pandas.DataFrame(data)

        self._df = df

    def save(self, name):
        """save dataframe in the path define in attributes
        :name: name of the user for filename

        """
        if self._df is not None and self._year is not None:
            filename = f'{name}_{self._year}'
            path = os.path.join(self.directory, filename)
            self._df.to_csv(path, index=False)

    def load(self, name, year, break_duration_mn):
        """load df from path

        """
        filename = f'{name}_{year}'
        path = os.path.join(self.directory, filename)
        try:
            self._df = pandas.read_csv(path)
        except FileNotFoundError:
            print('no file found')
        if 'worktime' not in self._df:
            self._df['worktime'] = '00:00'
        if 'day_balance' not in self._df:
            self._df['day_balance'] = '00:00'

        break_time = datetime.timedelta(minutes=break_duration_mn)
        worktimes = self._get_all_worktimes(break_time)
        print(worktimes)

        # for row in range(row_max):
            # worktime = self._get_day_worktime(row, break_time)
            # required_worktime = self._get_day_required_worktime(row, employment_rate)
            # day_balance = worktime - required_worktime 
            # balance += day_balance

        self._year = year

    def get_today_row(self):
        row = datetime.date.today().timetuple().tm_yday - 1
        return row

    def get_holiday_rows(self):
        workday_array = self.df.workday.values
        holliday_array = 1 - workday_array
        # rows = numpy.argwhere(holliday_array)
        rows = numpy.nonzero(holliday_array)
        return rows


    def check_balance(self, date, employment_rate, break_duration_mn, last_year_balance=datetime.timedelta(0)):
        balance = last_year_balance
        row_max = date.timetuple().tm_yday - 1
        break_time = datetime.timedelta(minutes=break_duration_mn)
        for row in range(row_max):
            worktime = self._get_day_worktime(row, break_time)
            required_worktime = self._get_day_required_worktime(row, employment_rate)
            day_balance = worktime - required_worktime 
            balance += day_balance
        return balance

    def get_today_worktime(self, break_duration_mn):
        break_time = datetime.timedelta(minutes=break_duration_mn)
        now = datetime.datetime.now()
        day = datetime.date.today()
        row = datetime.date.today().timetuple().tm_yday - 1

        start_time = datetime.datetime.combine(day, datetime.time.fromisoformat(self._df.at[row, 'AM_start']))
        end_time = datetime.datetime.combine(day, datetime.time.fromisoformat(self._df.at[row, 'AM_end']))
        if start_time < now:
            if end_time > now or end_time < start_time:
                end_time = now
            morning_worktime = end_time - start_time
        else:
            morning_worktime = 0
        if morning_worktime > break_time:
            morning_worktime = morning_worktime - break_time

        start_time = datetime.datetime.combine(day, datetime.time.fromisoformat(self._df.at[row, 'PM_start']))
        end_time = datetime.datetime.combine(day, datetime.time.fromisoformat(self._df.at[row, 'PM_end']))
        if start_time < now:
            if end_time > now or end_time < start_time:
                end_time = now
            afternoon_worktime = end_time - start_time
        else:
            afternoon_worktime = 0
        if afternoon_worktime > break_time:
            afternoon_worktime = afternoon_worktime - break_time

        day_worktime = morning_worktime + afternoon_worktime

        return day_worktime

    def get_today_balance(self, employment_rate, break_duration_mn):
        worktime = self.get_today_worktime(break_duration_mn)
        row = datetime.date.today().timetuple().tm_yday - 1
        required_worktime = self._get_day_required_worktime(row, employment_rate)
        balance = worktime - required_worktime
        return balance


    def _get_day_worktime(self, row, break_time):
        day = datetime.date.min # every day has the same hours, so it does not matter what day we take
        start_time = datetime.datetime.combine(day, datetime.time.fromisoformat(self._df.at[row, 'AM_start'])) # we have to create a datetime to use timedeltas
        end_time = datetime.datetime.combine(day, datetime.time.fromisoformat(self._df.at[row, 'AM_end']))
        morning_worktime = end_time - start_time
        if morning_worktime > break_time:
            morning_worktime = morning_worktime - break_time
        start_time = datetime.datetime.combine(day, datetime.time.fromisoformat(self._df.at[row, 'PM_start']))
        end_time = datetime.datetime.combine(day, datetime.time.fromisoformat(self._df.at[row, 'PM_end']))
        afternoon_worktime = end_time - start_time
        if afternoon_worktime > break_time:
            afternoon_worktime = afternoon_worktime - break_time
        day_worktime = morning_worktime + afternoon_worktime
        return day_worktime

    def _get_all_worktimes(self, break_time):
        worktimes = None
        return worktimes


    def _get_day_required_worktime(self, row, employment_rate):
        is_workday = self._df.at[row, 'workday']
        if is_workday:
            required_worktime = self.FULL_DAY_WORKTIME * employment_rate
        else:
            required_worktime = datetime.timedelta(0)
        return required_worktime



class Parameters(object):

    """allow to store and load parameters between session"""

    def __init__(self, name: str, **default_parameters):
        """create parameter object and check if folder exist

        :default_parameters: dict of default values
        :name:

        """
        self._default_parameters = default_parameters
        self._name = name

        directory = os.path.join(xdg.xdg_data_home(), APP_NAME)
        if not os.path.exists(directory):
            os.makedirs(directory)
        self._file_path = os.path.join(directory, name + '.json')

        def make_prop(name):
            def getter(self):
                return self._parameters[name]

            def setter(self, value):
                self._parameters[name] = value
                self._save_current_parameters()

            return property(getter, setter)

        self._parameters = dict()
        for name, value in default_parameters.items():
            self._parameters[name] = value
            setattr(Parameters,  name, make_prop(name))

        self._load_last_parameters()

    def _save_current_parameters(self):
        """save current parameters in a json file


        """
        try:
            with open(self._file_path, 'w') as myfile:
                json.dump(self._parameters, myfile)
        except IOError:
            print('could not access or find last parameter file')
        except TypeError:
            print(
                    'could not save parameters. TypeError.'
                    'probably because one object is not Json serializable')

    def _load_last_parameters(self):
        """load parameter from last saved file


        """
        try:
            with open(self._file_path, 'r') as myfile:
                last_parameters = json.load(myfile)
        except EOFError:
            print('last parameter file is probably empty..')
        except IOError:
            print('could not access or find last parameter file')
        except json.decoder.JSONDecodeError:
            print('json file is probably corrupted')
        else:
            for key, el in last_parameters.items():
                if key in self._parameters:
                    self._parameters[key] = el

    def restore_default(self):
        """TODO: restore default values


        """
        for name in self._parameters:
            setattr(self, name, self._default_parameters[name])

    def get_keys(self):
        """helper to get list of all parameters
        :returns: keys obj of all parameter names

        """
        return self._parameters.keys()

    def to_dict(self):
        """convert to a dictionnary
        :returns: dict

        """
        current_parameters = dict()
        for key in self._default_parameters:
            current_parameters[key] = getattr(self, key)
        return current_parameters


if __name__ == '__main__':
    main()
