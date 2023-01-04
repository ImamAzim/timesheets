import tkinter
from tkinter import ttk


from timesheets.views.base import MainMenu, TimeSheetView


def main():
    run_timesheet()


def run_timesheet():
    app = TimeSheetApp()
    app.start()

class TimeSheetApp(tkinter.Tk):

    def __init__(self):
        super().__init__()

        pandaframe = ttk.Frame(self)
        main_menu = MainMenu(self, debug=False)
        app_view = TimeSheetView(self, main_menu, pandaframe)
        pandaframe.pack(expand=True, fill=tkinter.BOTH)
        main_menu.pack(side=tkinter.LEFT)
        app_view.pack(side=tkinter.LEFT)
        app_view.load()
        app_view.show()
        app_view.check_balance()

    def start(self):
        self.mainloop()

if __name__ == '__main__':
    main()
