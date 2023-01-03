import os


import pandas
import xdg


def main():
    test()


def test():
    timesheet = TimeSheet(0.8)
    timesheet.create_new(2023, [])
    timesheet.save('test')


APP_NAME = 'timesheets'


class TimeSheet(object):

    """Docstring for TimeSheet. """

    def __init__(self, employement_rate):
        """TODO: to be defined.

        :employement_rate: float

        """
        self._employement_rate = employement_rate
        self._df = None
        directory = os.path.join(xdg.xdg_data_home(), APP_NAME)
        if not os.path.exists(directory):
            os.makedirs(directory)
        self._directory = directory

    def create_new(self, year, holidays):
        """create a new dataframe

        :year: int
        :holidays: list of date

        """
        self._year = year
        df = pandas.DataFrame()
        self._df = df

    def save(self, name):
        """save dataframe in the path define in attributes
        :path: to filename

        """
        if self._df is not None:
            pass

    def load(self, name):
        """load df from path
        :path: str to filename

        """
        pass

    def check_balance(self, date):
        balance = 0
        return balance


if __name__ == '__main__':
    main()
