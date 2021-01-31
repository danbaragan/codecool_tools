from colorama import Fore, Back, Style


class ProjectNamer:
    week_type = 'si'

    def __init__(self, week_type='si', week_number=None):
        if week_number is not None:
            if not 1 <= week_number <= 6:
                raise ValueError(f'Choose a week between 1 and 6')
            self.week_number = week_number - 1
        else:
            self.week_number = None  # all weeks
        
        self.week_type = week_type


    def cycle_weeks(self):
        if self.week_number is not None:
            yield self.week_number
        else:
            yield from range(6)


    def cycle_names(self, week):
        names_by_week = self.PROJECT_NAMES[self.week_type]
        for prj in names_by_week[week]:
            yield prj

    @property
    def module_name(self):
        return self.WEEK_NAME[self.week_type]


class PgProjectNamer(ProjectNamer):
    SI_PROJECT_NAMES = [
        [],
        ['git-started-general', 'lets-get-qualified-general', 'setup-python-general',
         'hello-world-python', 'simple-calculator-python', 'project-rewrite-python'],
        ['ideabank-python', 'sorting-flowchart-python', 'seti-python', 'gitting-around-general',
         'hello-console-python',],
        ['game-inventory-python', 'guessing-game-python', 'string-theory-python',
         'memory-game-python', ],
        ['filetree-python', 'game-statistics-python', 'true-detective-python',
         'embroidery-python'],
        ['keymaker-python'],
    ]
    TW_PROJECT_NAMES = [
        [],
        ['hangman-python'],
        ['tic-tac-toe-python'],
        ['battleship-python'],
        ['secure-erp-python', 'code-taboo-gambling-python'],
        ['roguelike-game-python'],
    ]
    WEEK_NAME = {
        'si': 'ProgBasics SI',
        'tw': 'ProgBasics TW',
    }
    PROJECT_NAMES = {
        'si': SI_PROJECT_NAMES,
        'tw': TW_PROJECT_NAMES,
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


### helpers

def print_projects(namer, github_account=None):
    for week in namer.cycle_weeks():
        print(f'Projects for {Fore.YELLOW}{namer.module_name}{week+1}{Style.RESET_ALL}:')
        for prj in namer.cycle_names(week):
            project_name = prj
            if github_account:
                project_name += '-' + github_account
            print(project_name)
