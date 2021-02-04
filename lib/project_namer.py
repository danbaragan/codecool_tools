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


class PbProjectNamer(ProjectNamer):
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


class WebProjectNamer(ProjectNamer):
    SI_PROJECT_NAMES = [
        ['onboarding-web-general', 'curling-general', 'flask-note-python',
         'request-counter-python', 'super-sprinter-3000-python'],
        ['setup-postgresql-python', 'application-process-python',
         'python-on-steroids-python', 'css-layouts-general'],
        ['codewars-sql-7-kyu-general', 'northwind-traders-python',
         'syringe-python', 'flying-circus-python', 'branched-off-general'],
        ['multi-color-buttons-javascript', 'minesweeper-javascript',
         'codewars-javascript-7-kyu-general', 'deface-general',
         'metamorphosis-javascript', 'step-by-step-python'],
        ['callback-hell-javascript', 'untrusted-javascript',
         'color-picker-javascript', 'api-wars-python',],
        ['codecool-series-python', 'html-formatter-general',
         'api-wars-deployment-general', 'codewars-javascript-6-kyu-general',
         'codewars-sql-6-kyu-general', 'responsive-rainbow-general'],
    ]
    TW_PROJECT_NAMES = [
        ['ask-mate-1-python'],
        ['agile-general', 'ask-mate-2-python'],
        ['ask-mate-3-python'],
        ['freestyle-javascript-game-javascript', 'code-taboo-sorting-javascript'],
        ['proman-1-python'],
        ['proman-2-python'],
    ]
    WEEK_NAME = {
        'si': 'Web SI',
        'tw': 'Web TW',
    }
    PROJECT_NAMES = {
        'si': SI_PROJECT_NAMES,
        'tw': TW_PROJECT_NAMES,
    }


class OopjProjectNamer(ProjectNamer):
    SI_PROJECT_NAMES = [
        ['onboarding-oop-general', 'setup-java-general', 'hello-world-oop-java',
         'five-in-a-row-java', 'codewars-java-7-kyu-general', 'street-writer-java',
         'enigma-java'],
        ['car-race-java', 'geometry-java', 'waste-recycling-java', 'rewrite-dynamic-array-java',
         'build-your-builder-java', 'codewars-java-6-kyu-general'],
        ['planning-motors-general', 'rewrite-linkedlist-java',
         'history-java', 'life-of-the-ants-java'],
        ['histogram-java', 'book-db-java', 'rewrite-hashtable-java',
         'wardrobe-java', 'codecoolers-everywhere-python'],
        ['hacker-news-java', 'kitchen-helpers-java', 'stock-trader-java'],
        ['six-handshakes-java', 'gladiator-java', 'polyglot-club-general', 'fibonacci-variants-java'],
    ]
    TW_PROJECT_NAMES = [
        ['remake-progbasics-game-java'],
        ['process-watch-java'],
        ['dungeon-crawl-1-java'],
        ['dungeon-crawl-2-java'],
        ['codecool-shop-1-java'],
        ['codecool-shop-2-java'],
    ]
    WEEK_NAME = {
        'si': 'OOP/Java SI',
        'tw': 'OOP/Java TW',
    }
    PROJECT_NAMES = {
        'si': SI_PROJECT_NAMES,
        'tw': TW_PROJECT_NAMES,
    }


class AdvProjectNamer(ProjectNamer):
    SI_PROJECT_NAMES = [
        [],
        [],
        [],
        [],
        [],
        [],
    ]
    TW_PROJECT_NAMES = [
        [],
        [],
        [],
        [],
        [],
        [],
    ]
    WEEK_NAME = {
        'si': 'OOP SI',
        'tw': 'OOP TW',
    }
    PROJECT_NAMES = {
        'si': SI_PROJECT_NAMES,
        'tw': TW_PROJECT_NAMES,
    }


### helpers

def namer_factory(module):
    if module == 'pb':
        return PbProjectNamer
    elif module == 'web':
        return WebProjectNamer
    elif module == 'oopj':
        return OopjProjectNamer
    elif module == 'adv':
        raise NotImplementedError
    else:
        raise NotImplementedError


def print_projects(namer, github_account=None):
    for week in namer.cycle_weeks():
        print(f'Projects for {Fore.YELLOW}{namer.module_name}{week+1}{Style.RESET_ALL}:')
        for prj in namer.cycle_names(week):
            project_name = prj
            if github_account:
                project_name += '-' + github_account
            print(project_name)
