import csv
from pathlib import Path

import colorama
from colorama import Fore, Back, Style


# TODO This is very coupled with the main loop in si_work.py script
# While some of the modules in lib could be reused, I doubt this will
# thus placing in here is unfortunate; but I don't want to clobber the script file itself
class Printer:
    BASE_HEADER = ['name', 'github']
    BASE_WIDTHS = [22, 16]

    def __init__(self):
        self.student_activities = {}

    def __enter__(self):
        raise NotImplementedError

    def __exit__(self, type, value, traceback):
        raise NotImplementedError

    def module_line(self, name, week):
        pass

    def inter_header(self, *args, **kwargs):
        pass

    def student_cells(self, name, github, *args):
        self.student_name = name
        self.student_github = github

    def activity_cells(self, project, activity):
        self.student_activities[project] = self._activity2str(activity)

    def flush_row(self):
        self.student_activities = {}
        self.student_name = self.student_github = ''


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
    def student_cells(self, name, *args):
        print(f'{Fore.YELLOW}{name}{Style.RESET_ALL}:')


    def activity_cells(self, project, activity):
        activity_str = self._activity2str(activity)
        print(f'{project:<50}{activity_str}')


    def flush_row(self, *args, **kwargs):
        # line printer only adds a new line on row flush as it printed 'cells' one by one
        print()


class TablePrinter(TtyPrinter):

    def inter_header(self, project_names):
        self.width = max(map(len, project_names)) + 1 if project_names else 0
        header_str = f'{self.BASE_HEADER[0]:^{self.BASE_WIDTHS[0]}}{self.BASE_HEADER[1]:^{self.BASE_WIDTHS[1]}}'
        for h in project_names:
            header_str += f'{h:^{self.width}}'
        print(header_str)


    def flush_row(self):
        # reset the student activities for this row
        row_str = (f'{Fore.YELLOW}{self.student_name:<{self.BASE_WIDTHS[0]}}'
                   f'{Style.RESET_ALL}{self.student_github:^{self.BASE_WIDTHS[1]}}')
        for activity in self.student_activities.values():
            row_str += activity
        print(row_str)
        super().flush_row()


class CsvPrinter(Printer):
    BASE_HEADER = ['module', 'week'] + Printer.BASE_HEADER

    def __init__(self, script_name):
        super().__init__()
        self.out_path = Path('data') / f'{script_name}_out.csv'


    def __enter__(self):
        if self.out_path.exists():
            self.out_path.rename(str(self.out_path) + '.old')
        self.out_file = open(self.out_path, "w")
        self.csv = csv.writer(self.out_file)
        return self


    def __exit__(self, type, value, traceback):
        self.out_file.close()
        print(f'{self.out_path} written')


    def module_line(self, name, week):
        self.module = name
        self.week = week


    # this is not an actual csv header, but a line that repeats every time week changes and thus project names
    def inter_header(self, project_names):
        row = self.BASE_HEADER + project_names
        self.csv.writerow(row)


    def flush_row(self):
        row = [self.module, self.week, self.student_name, self.student_github]
        row.extend(self.student_activities.values())
        self.csv.writerow(row)
        super().flush_row()


    def _activity2str(self, activity):
        activity_str = 'unknown err'
        if activity == -1:
            activity_str = 'not started'
        elif activity == 1:
            activity_str = 'none'
        elif type(activity) in [int, str]:
            activity_str = activity

        return activity_str

### helpers

def printer_factory(display, script_name):
    if display == 'lines':
        return LinePrinter()
    elif display == 'table':
        return TablePrinter()
    elif display == 'csv':
        return CsvPrinter(Path(script_name).stem)
