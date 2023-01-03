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


    def __init__(self, root, main_menu, name='timesheet'):
        super().__init__(root, main_menu, name, user_name=os.getlogin(), year=2023, employement_rate=1)


        frames = dict()
        buttons = dict()
        entries = dict()
        labels = dict()

        entry_names = ('user_name', 'year', 'employement_rate')

        frames['frame 1'] = ttk.LabelFrame(self)
        parent = frames['frame 1']
        for name, var in self._app_parameters_var.items():
            if name in entry_names:
                labels[name] = ttk.Label(parent, text=name)
                entries[name] = ttk.Entry(parent, textvariable=var)
        buttons['new'] = ttk.Button(parent, text='new', command=self.create_new)
        buttons['save'] = ttk.Button(parent, text='save', command=self.save)
        buttons['load'] = ttk.Button(parent, text='load', command=self.load)
        buttons['show'] = ttk.Button(parent, text='show', command=self.show)

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

        self.print('welcome to the timesheets app\n')
        employement_rate = float(self._app_parameters_var['employement_rate'].get())

        self._timesheet = TimeSheet(employement_rate)

    def create_new(self):
        year = int(self._app_parameters_var['year'].get())
        self._timesheet.create_new(year, [])

    def save(self):
        name = self._app_parameters_var['user_name'].get()
        self._timesheet.save(name)

    def load(self):
        name = self._app_parameters_var['user_name'].get()
        year = int(self._app_parameters_var['year'].get())
        self._timesheet.load(name, year)

    def show(self):
        df = self._timesheet.df
        print(df)
        window = tkinter.Toplevel()
        table = pandastable.Table(window, dataframe=df)
        table.copyIndex()
        table.show()


def manual_test():
    root = tkinter.Tk()
    main_menu = MainMenu(root, debug=True)
    app_view = TimeSheetView(root, main_menu)
    main_menu.grid(row=0, column=0)
    app_view.grid(row=0, column=1)
    root.mainloop()

if __name__ == '__main__':
    manual_test()
