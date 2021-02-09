import colorama
from colorama import Fore, Back, Style


# TODO This is very coupled with the main loop in si_work.py script
# While some of the modules in lib could be reused, I doubt this will
# thus placing in here is unfortunate; but I don't want to clobber the script file itself
class Printer:
    BASE_HEADER = ['Name', 'github']
    BASE_WIDTHS = [20, 12]

    def __init__(self):
        self.student_activities = {}

    def __enter__(self):
        raise NotImplementedError

    def __exit__(self, type, value, traceback):
        raise NotImplementedError

    def module_line(self, name, week):
        pass

    def header(self, *args, **kwargs):
        pass

    def student_cell(self, *args, **kwargs):
        pass


class TtyPrinter(Printer):
    width = 25

    def __enter__(self):
        colorama.init()  # noop for any system but windows...
        return self

    def __exit__(self, type, value, traceback):
        colorama.deinit()

    def module_line(self, name, week):
        print(f'Projects for {Fore.YELLOW}{name}{week+1}{Style.RESET_ALL}:\n')

    def _activity2str(self, activity):
        activity_str = 'unknown err'
        activity_str = f'{Fore.RED}{activity_str:^{self.width}}{Style.RESET_ALL}'
        if type(activity) is str:
            activity_str = f'{Fore.RED}{activity:^{self.width}}{Style.RESET_ALL}'
        elif activity == -1:
            not_started = 'not started'
            activity_str = f'{Fore.RED}{not_started:^{self.width}}{Style.RESET_ALL}'
        elif activity <= 1:
            activity_str = f'{Fore.RED}{activity:^{self.width}}{Style.RESET_ALL}'
        elif activity > 1:
            activity_str = f'{Fore.GREEN}{activity:^{self.width}}{Style.RESET_ALL}'

        return activity_str



class LinePrinter(TtyPrinter):
    def student_cell(self, name):
        print(f'{Fore.YELLOW}{name}{Style.RESET_ALL}:')


    def activity_cell(self, project, activity):
        activity_str = self._activity2str(activity)
        print(f'{project:<50}{activity_str}')


    def flush_row(self, *args, **kwargs):
        # line printer only adds a new line on row flush as it printed 'cells' one by one
        print()


class TablePrinter(TtyPrinter):

    def header(self, project_names):
        # if there are 2 adiacent max length proj names, the column will touch
        # and be hard to copy paste.
        # still I'd rather leave it like this
        # and save that extra space to fit as much as possible on one row
        self.width = max(map(len, project_names)) if project_names else 0
        header_str = f'{self.BASE_HEADER[0]:^{self.BASE_WIDTHS[0]}}{self.BASE_HEADER[1]:^{self.BASE_WIDTHS[1]}}'
        for h in project_names:
            header_str += f'{h:^{self.width}}'
        print(header_str)


    def activity_cell(self, project, activity):
        self.student_activities[project] = self._activity2str(activity)


    def flush_row(self, name, github):
        # reset the student activities for this row
        row_str = f'{Fore.YELLOW}{name:<{self.BASE_WIDTHS[0]}}{Style.RESET_ALL}{github:^{self.BASE_WIDTHS[1]}}'
        for activity in self.student_activities.values():
            row_str += activity
        print(row_str)
        self.student_activities = {}


class CsvPrinter(Printer):
    pass



### helpers

def printer_factory(display):
    if display == 'lines':
        return LinePrinter
    elif display == 'table':
        return TablePrinter
    elif display == 'csv':
        raise NotImplementedError
