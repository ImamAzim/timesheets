import os
import json


import pandas
import xdg


def main():
    test()


def test():
    timesheet = TimeSheet(0.8)
    timesheet.load('test', 2023)
    print(timesheet)
    # timesheet.create_new(2023, [])
    # timesheet.save('test')


APP_NAME = 'timesheets'


class TimeSheet(object):

    """Docstring for TimeSheet. """

    def __init__(self, employement_rate=1):
        """TODO: to be defined.

        :employement_rate: float

        """
        self._employement_rate = employement_rate
        self._df = None
        self._year = None
        directory = os.path.join(xdg.xdg_data_home(), APP_NAME)
        if not os.path.exists(directory):
            os.makedirs(directory)
        self._directory = directory

    @property
    def df(self):
        return self._df

    def __repr__(self):
        text = self._df.to_string()
        return text

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
        :name: name of the user for filename

        """
        if self._df is not None and self._year is not None:
            filename = f'{name}_{self._year}'
            path = os.path.join(self._directory, filename)
            self._df.to_csv(path)

    def load(self, name, year):
        """load df from path

        """
        filename = f'{name}_{year}'
        path = os.path.join(self._directory, filename)
        self._df = pandas.read_csv(path)
        self._year = year

    def check_balance(self, date):
        balance = 0
        return balance


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
