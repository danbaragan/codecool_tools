#!/usr/bin/env python

from dotenv import load_dotenv
load_dotenv()
import argparse
import concurrent.futures
import os
from pathlib import Path
from pprint import pprint as pp
import sys

import colorama
from colorama import Fore, Back, Style
from agithub.GitHub import GitHub

from lib.project_namer import PgProjectNamer, print_projects
from lib.data_reader import Reader


DATA_FILE = Path('data') / 'students.csv'

hub_client = GitHub(token=os.getenv('TOKEN'))


def get_commits_activity_from_github(project):
    # https://docs.github.com/en/rest/reference/repos#get-a-repository

    # TODO this will go to the default branch == development; what if all their code is on master? or main?
    # feed `sha=master` to get() to specify other branch than default
    status, resp = hub_client.repos.CodecoolGlobal[project].commits.get()
    activity = resp  # in case none of the below - assume it is some error inside the response

    if status == 404:
        activity = -1
    elif status == 200:
        activity = len(resp)
    return activity


if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog='si_work.py',
    description=f"""Show what work in terms of commits sudets did during their SI week
    """,
    epilog="You should have data/students.csv file with a header like `name,github`")

    parser.add_argument('-t', '--type', choices=['si', 'tw'], default='si',
        help='week type; si or tw; default si')
    parser.add_argument('week', type=int, nargs='?',
        choices=[1, 2, 3, 4, 5, 6], default=None,
        help='Week number to show; All if empty; default empty')

    args = parser.parse_args()
    # data_path = Path(DATA_FILE)
    if not DATA_FILE.exists():
        print(f'No {DATA_FILE} found!\n\n')
        parser.print_help()
        sys.exit(-1)

    # noop for anything but windows...
    colorama.init()
    namer = PgProjectNamer(args.type, args.week)

    students = []
    # Expecting a csv of form: name,github
    with Reader(DATA_FILE, has_header=True) as rd:
        for row in rd:
            students.append(row)

    for week in namer.cycle_weeks():
        print(f'Projects for {Fore.YELLOW}{namer.module_name}{week+1}{Style.RESET_ALL}:')
        for student in students:
            print(f'{Fore.YELLOW}{student["name"]}{Style.RESET_ALL}:')

            student_projects = []
            for prj in namer.cycle_names(week):
                project = f'{prj}-{student["github"]}'
                student_projects.append(project)

            with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
                future_to_url = {executor.submit(get_commits_activity_from_github, prj): prj for prj in student_projects}

                for future_activity in concurrent.futures.as_completed(future_to_url):
                    project = future_to_url[future_activity]
                    try:
                        activity = future_activity.result()
                    except Exception as e:
                        activity = str(e)

                    if activity == -1:
                        activity_str = f'{Fore.RED}repo not started{Style.RESET_ALL}'
                    elif activity <= 1:
                        activity_str = f'{Fore.RED}{activity}{Style.RESET_ALL}'
                    elif activity > 1:
                        activity_str = f'{Fore.GREEN}{activity}{Style.RESET_ALL}'
                    else:
                        activity_str = f'{Fore.RED}{activity}{Style.RESET_ALL}'

                    print(f'{project}: {activity_str}')
            print()
        print()

    # Don't mind improper program exit - this will just let windows consoles in a messed up state
    # but windows users close consoles on sight so it's cheaper for the code complexity to leave that out
    colorama.deinit()