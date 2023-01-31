import sys
import tkinter
from tkinter.scrolledtext import ScrolledText
from tkinter import filedialog, messagebox
from tkinter import ttk
import datetime
import os
from functools import partial


import pandastable
from timesheets.models.base import Parameters, TimeSheet


def main():
    pass


class AppView(ttk.LabelFrame):

    """Generic App View. it can be inherited to define specific App"""

    def __init__(self, parent, main_menu, name, **app_var_default_values):
        """

        :parent: tkinter parent window
        main_menu: a view than contains quit button, text display, etc...

        """
        super().__init__(parent, text=name)

        self._parent = parent
        self._controller = None
        self._main_menu = main_menu
        self._name = name

        self._app_parameters = Parameters(name, **app_var_default_values)
        self._app_parameters_var = dict()
        for key in self._app_parameters.get_keys():
            self._app_parameters_var[key] = tkinter.StringVar()
            self._app_parameters_var[key].set(getattr(self._app_parameters, key))
            self._app_parameters_var[key].trace_add('write', partial(self._trace_when_var_is_updated, key=key))

    def _trace_when_var_is_updated(self, var, index, mode, key):
        setattr(self._app_parameters, key, self._app_parameters_var[key].get())

    def print(self, text):
        text = f'{self._name}:\n{text}'
        self._main_menu.print(text)


class MainMenu(ttk.Frame):

    """a main menu than can be appended to an app view"""

    def __init__(self, root, debug=False):
        super().__init__(root)
        self._root = root
        display = ScrolledText(self, width=60, height=20)
        quit_button = ttk.Button(
                self,
                text='quit',
                command=self.quit,
                )

        display.pack(fill=tkinter.BOTH, expand=True)
        quit_button.pack(fill=tkinter.BOTH)
        redir = RedirectText(self)
        sys.stdout = redir
        if not debug:
            sys.stderr = redir

        self._display = display
        default_metadata = dict(
                operator=os.getlogin(),
                )

    def print(self, text):
        """method to print some message on the display

        :text: TODO
        :returns: TODO

        """
        self._display.insert(tkinter.END, text)

    def quit(self):
        for child in self._root.winfo_children():
            if child is not self:
                child.quit()
        self._root.quit()


class RedirectText:

    def __init__(self, main_menu):
        self._main_menu = main_menu

    def write(self, text):
        self._main_menu.print(text)

    def flush(self):
        pass


class TimeSheetView(AppView):


    def __init__(self, root, main_menu, pandaframe, name='timesheet'):
        super().__init__(root, main_menu, name, user_name=os.getlogin(), year=2023, employment_rate=1, path='', last_year_balance='00:00', break_duration_mn=10)

        self._root = root


        frames = dict()
        buttons = dict()
        entries = dict()
        labels = dict()

        self.table = None

        entry_names = ('user_name', 'year', 'employment_rate', 'last_year_balance', 'break_duration_mn')

        frames['frame 1'] = ttk.LabelFrame(self)
        parent = frames['frame 1']
        for name, var in self._app_parameters_var.items():
            if name in entry_names:
                labels[name] = ttk.Label(parent, text=name)
                entries[name] = ttk.Entry(parent, textvariable=var)
        buttons['path'] = ttk.Button(parent, textvariable=self._app_parameters_var['path'], command=self._change_path, width=30)
        buttons['new'] = ttk.Button(parent, text='new', command=self.create_new)
        buttons['save'] = ttk.Button(parent, text='save', command=self.save)
        buttons['load'] = ttk.Button(parent, text='load', command=self.load)
        buttons['show'] = ttk.Button(parent, text='show', command=self.show)
        buttons['check balance'] = ttk.Button(parent, text='check balance', command=self.check_balance)
        buttons['today balance'] = ttk.Button(parent, text='today balance', command=self.show_today_balance)
        self._balance_display = ttk.Label(parent, anchor=tkinter.CENTER, foreground='white')

        for name, frame in frames.items():
            frame.pack(fill=tkinter.BOTH, expand=True)
        row = 0
        for name, var in self._app_parameters_var.items():
            if name in entry_names:
                labels[name].grid(column=0, row=row)
                entries[name].grid(column=1, row=row)
                row += 1
        for button in buttons.values():
            button.grid(column=0, row=row, columnspan=2, sticky='ew')
            row += 1
        self._balance_display.grid(column=0, row=row, columnspan=2, sticky='ew')
        row += 1


        # self._pandasframe = frames['table']
        self._pandasframe = pandaframe

        self.print('welcome to the timesheets app\n')

        self._timesheet = TimeSheet()
        self._timesheet.directory = self.timesheet_folder

    @property
    def timesheet_folder(self):
        return self._app_parameters_var['path'].get()

    @timesheet_folder.setter
    def timesheet_folder(self, new_path):
        self._app_parameters_var['path'].set(new_path)

    def create_new(self):
        year = int(self._app_parameters_var['year'].get())
        self._timesheet.create_new(year, [])

    def save(self):
        name = self._app_parameters_var['user_name'].get()
        self._timesheet.save(name)
        self.check_balance()

    def load(self):
        name = self._app_parameters_var['user_name'].get()
        year = int(self._app_parameters_var['year'].get())
        break_duration_mn = int(self._app_parameters_var['break_duration_mn'].get())
        employment_rate = float(self._app_parameters_var['employment_rate'].get())
        self._timesheet.load(name, year, break_duration_mn, employment_rate)

    def show(self):
        df = self._timesheet.df
        # window = tkinter.Toplevel()
        window = self._pandasframe
        table = pandastable.Table(window, dataframe=df)
        table.show()
        table.redraw()
        row = self._timesheet.get_today_row()
        table.movetoSelection(row=row)
        holiday_rows = self._timesheet.get_holiday_rows()
        table.setRowColors(rows=holiday_rows, clr='gray', cols='all')
        table.redraw()
        table.autoResizeColumns()
        x = max(743, sum(list(table.columnwidths.values())) + 100)
        y= 700
        self._root.geometry(f'{x}x{y}')
        self.table = table

    def check_balance(self):
        employment_rate = float(self._app_parameters_var['employment_rate'].get())
        date = datetime.date.today()

        last_year_balance_str = self._app_parameters_var['last_year_balance'].get()
        if last_year_balance_str[0] == '-':
            last_year_balance_str = last_year_balance_str[1:]
            negative_balance = True
        else:
            negative_balance = False
        last_year_datetime = datetime.datetime.combine(datetime.date.min, datetime.time.fromisoformat(last_year_balance_str))
        ref = datetime.datetime.min
        last_year_balance = last_year_datetime - ref
        if negative_balance:
            last_year_balance = - last_year_balance

        break_duration_mn = int(self._app_parameters_var['break_duration_mn'].get())

        balance = self._timesheet.check_balance(date, employment_rate, break_duration_mn, last_year_balance)
        self.update_balance_display(balance)

    def update_balance_display(self, balance):
        if balance < datetime.timedelta(0):
            text = str(-balance)
            color = 'red'
        else:
            text = str(balance)
            color = 'green'
        self._balance_display['text'] = text
        self._balance_display['background'] = color

    def show_today_balance(self):
        break_duration_mn = int(self._app_parameters_var['break_duration_mn'].get())
        employment_rate = float(self._app_parameters_var['employment_rate'].get())
        balance = self._timesheet.get_today_balance(employment_rate, break_duration_mn)
        if balance < datetime.timedelta(0):
            text = '-' + str(-balance)
        else:
            text = str(balance)
        self.print(text)

    def _change_path(self):
        path = filedialog.askdirectory(title='timesheet folder', initialdir=self._timesheet.directory)
        if path:
            self.timesheet_folder = path
            self._timesheet.directory = path


def manual_test():
    root = tkinter.Tk()
    pandaframe = ttk.Frame(root)
    main_menu = MainMenu(root, debug=True)
    app_view = TimeSheetView(root, main_menu, pandaframe)
    pandaframe.pack(expand=True, fill=tkinter.BOTH)
    main_menu.pack(side=tkinter.LEFT)
    app_view.pack(side=tkinter.LEFT)
    app_view.load()
    app_view.show()
    app_view.check_balance()
    root.mainloop()

if __name__ == '__main__':
    manual_test()
