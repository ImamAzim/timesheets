def main():
    pass

class TimeSheet(object):

    """Docstring for TimeSheet. """

    def __init__(self, employement_rate):
        """TODO: to be defined.

        :employement_rate: float

        """
        self._employement_rate = employement_rate
        self._df = None
        self.path = None

    def create_new(self, year, holidays):
        """create a new dataframe

        :year: int
        :holidays: list of date

        """
        df = None
        self._df = df

    def save(self):
        """save dataframe in the path define in attributes

        """
        pass

    def load(self):
        """load df from path

        """
        pass

    def check_balance(self, date):
        balance = 0
        return balance


if __name__ == '__main__':
    main()
