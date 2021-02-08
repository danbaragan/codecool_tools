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

from lib.project_namer import namer_factory, print_projects
from lib.data_reader import Reader


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
    elif status == 401:
        print(f'{Fore.RED}{resp["message"]}{Style.RESET_ALL}')
        # we bail out from a thread in the name of the entire process!
        sys.exit(1)
    elif status == 403:
        raise PermissionError(resp['message'])
    else:
        raise RuntimeError(resp)

    return activity


if __name__ == '__main__':
    script_name = Path(__file__).stem
    script_name_ext = Path(__file__).name
    parser = argparse.ArgumentParser(prog=script_name_ext,
    description="""Show what work in terms of commits sudets did during their SI week""",
    epilog=f"""You should have data/{script_name}_si_work_<module>_students.csv file
    with a header like `name,github`;
    e.g. for oop Java module, have data/{script_name}_oopj_students.csv""")

    parser.add_argument('-t', '--type', choices=['si', 'tw'], default='si',
        help='week type; si or tw; default si')
    parser.add_argument('-d', '--display', choices=['lines', 'table'], default='lines',
        help='display results; line by line or in a table; default: lines')
    parser.add_argument('module', nargs=1, choices=['pb', 'web', 'oopj', 'oopc', 'adv'],
        help='module we inquire repo information from')
    parser.add_argument('week', type=int, nargs='?',
        choices=[1, 2, 3, 4, 5, 6], default=None,
        help='Week number to show; All if empty; default empty')

    args = parser.parse_args()
    data_file = Path('data') / f'{script_name}_{args.module[0]}_students.csv'
    if not data_file.exists():
        print(f'No {data_file} found!\n\n')
        parser.print_help()
        sys.exit(-1)

    namer = namer_factory(args.module[0])(args.type, args.week)

    # noop for anything but windows...
    colorama.init()

    students = []
    # Expecting a csv of form: name,github
    with Reader(data_file, has_header=True) as rd:
        for row in rd:
            students.append(row)

    header_base = ['Name', 'github']
    for week in namer.cycle_weeks():
        print(f'Projects for {Fore.YELLOW}{namer.module_name}{week+1}{Style.RESET_ALL}:\n')

        header = header_base + list(namer.cycle_names(week))
        if args.display == 'table':
            header_str = f'{header[0]:^20}{header[1]:^12}'
            for h in header[2:]:
                header_str += f'{h:^25}'
            print(header_str)

        for student in students:
            if args.display == 'lines':
                print(f'{Fore.YELLOW}{student["name"]}{Style.RESET_ALL}:')

            student_repos_activity = {}
            student_repos_activity_strs = {}
            project_name2repo = {}
            for prj in namer.cycle_names(week):
                project = f'{prj}-{student["github"]}'
                project_name2repo[prj] = project
                student_repos_activity[prj] = -1
                student_repos_activity_strs[prj] = ''

            with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
                future_to_url = {
                    executor.submit(get_commits_activity_from_github, project_name2repo[prj_name]):
                    prj_name for prj_name in project_name2repo
                }

                futures = concurrent.futures.as_completed(future_to_url, timeout=6)
                # Gather this in any order but write them to the dict with insertion ordered keys
                for future_activity in futures:
                    project = future_to_url[future_activity]
                    try:
                        activity = future_activity.result()
                    except Exception as e:
                        activity = str(e)
                    student_repos_activity[project] = activity

            # Dispaly them in the order of the initial dict keys
            for project, activity in student_repos_activity.items():
                project_repo = project_name2repo[project]

                activity_str = 'unknown err'
                activity_str = f'{Fore.RED}{activity_str:^25}{Style.RESET_ALL}'
                if type(activity) is str:
                    activity_str = f'{Fore.RED}{activity:^25}{Style.RESET_ALL}'
                elif activity == -1:
                    not_started = 'not started'
                    activity_str = f'{Fore.RED}{not_started:^25}{Style.RESET_ALL}'
                elif activity <= 1:
                    activity_str = f'{Fore.RED}{activity:^25}{Style.RESET_ALL}'
                elif activity > 1:
                    activity_str = f'{Fore.GREEN}{activity:^25}{Style.RESET_ALL}'

                if args.display == 'lines':
                    print(f'{project_repo:<50}{activity_str}')
                elif args.display == 'table':
                    student_repos_activity_strs[project] = activity_str
            if args.display == 'table':
                row_str = f'{Fore.YELLOW}{student["name"]:<20}{Style.RESET_ALL}{student["github"]:^12}'
                for prj, activity in student_repos_activity_strs.items():
                    row_str += activity
                print(row_str)
            if args.display == 'lines':
                print()
        print()

    # Don't mind improper program exit - this will just let windows consoles in a messed up state
    # but windows users close consoles on sight so it's cheaper for the code complexity to leave that out
    colorama.deinit()