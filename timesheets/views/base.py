import sys
import tkinter
from tkinter.scrolledtext import ScrolledText
from tkinter import filedialog, messagebox
from tkinter import ttk
import datetime
import os
from functools import partial


import pandastable
from timesheets.models.base import Parameters


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

    @property
    def controller(self):
        return self._controller

    @controller.setter
    def controller(self, controller):
        self._controller = controller

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
        super().__init__(root, main_menu, name)

        frames = dict()
        buttons = dict()

        frames['frame 1'] = ttk.LabelFrame(self)
        parent = frames['frame 1']
        buttons['button 1'] = ttk.Button(parent, text='test', command=self.test)

        for name, frame in frames.items():
            frame['text'] = name
            frame.pack(fill=tkinter.BOTH, expand=True)
        for button in buttons.values():
            button.pack(fill=tkinter.BOTH, expand=True)

        self.print('welcome to the timesheets app\n')

    def test(self):
        self.print('test')


def manual_test():
    root = tkinter.Tk()
    main_menu = MainMenu(root, debug=True)
    app_view = TimeSheetView(root, main_menu)
    from timesheets.models.base import TimeSheet
    from timesheets.controllers.base import TimeSheetController
    timesheet = TimeSheet()
    app_controller = TimeSheetController(app_view, timesheet)
    app_view.controller = app_controller
    main_menu.grid(row=0, column=0)
    app_view.grid(row=0, column=1)
    root.mainloop()

if __name__ == '__main__':
    manual_test()
