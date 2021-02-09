#!/usr/bin/env python

from logging import disable
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


def process_batch(project2repo):
    # create a dict with  repo_base_name -> activity in the proper order
    student_repos_activity = {prj:-1 for prj in project2repo}
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        future_to_url = {
            executor.submit(get_commits_activity_from_github, project2repo[prj_name]):
            prj_name for prj_name in project2repo
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
    
    return student_repos_activity


def get_activity_str(activity, width):
    activity_str = 'unknown err'
    activity_str = f'{Fore.RED}{activity_str:^{width}}{Style.RESET_ALL}'
    if type(activity) is str:
        activity_str = f'{Fore.RED}{activity:^{width}}{Style.RESET_ALL}'
    elif activity == -1:
        not_started = 'not started'
        activity_str = f'{Fore.RED}{not_started:^{width}}{Style.RESET_ALL}'
    elif activity <= 1:
        activity_str = f'{Fore.RED}{activity:^{width}}{Style.RESET_ALL}'
    elif activity > 1:
        activity_str = f'{Fore.GREEN}{activity:^{width}}{Style.RESET_ALL}'

    return activity_str


def get_table_header_str(projects, width):
    header = ['Name', 'github'] + projects
    header_str = f'{header[0]:^20}{header[1]:^12}'
    for h in header[2:]:
        header_str += f'{h:^{width}}'
    return header_str

def get_table_row_str(name, github, student_repos_activity_strs):
    row_str = f'{Fore.YELLOW}{name:<20}{Style.RESET_ALL}{github:^12}'
    for activity in student_repos_activity_strs.values():
        row_str += activity

    return row_str


def setup_args_parser(script_name):
    script_name_ext = Path(__file__).name
    parser = argparse.ArgumentParser(
        prog=script_name_ext,
        description="""Show what work in terms of commits sudets did during their SI week""",
        epilog=f"""You should have data/{script_name}_si_work_<module>_students.csv file
        with a header like `name,github`;
        e.g. for oop Java module, have data/{script_name}_oopj_students.csv"""
    )

    parser.add_argument('-t', '--type', choices=['si', 'tw'], default='si',
        help='week type; si or tw; default si')
    parser.add_argument('-d', '--display', choices=['lines', 'table'], default='table',
        help='display results; line by line or in a table; default: table')
    parser.add_argument('module', nargs=1, choices=['pb', 'web', 'oopj', 'oopc', 'adv'],
        help='module we inquire repo information from')
    parser.add_argument('weeks', type=int, nargs='+',
        choices=[1, 2, 3, 4, 5, 6],
        help='Week numbers to show')

    return parser


if __name__ == '__main__':
    script_name = Path(__file__).stem
    parser = setup_args_parser(script_name)
    args = parser.parse_args()

    data_file = Path('data') / f'{script_name}_{args.module[0]}_students.csv'
    if not data_file.exists():
        print(f'No {data_file} found!\n\n')
        parser.print_help()
        sys.exit(-1)

    namer = namer_factory(args.module[0])(args.type, args.weeks)
    # noop for anything but windows...
    colorama.init()

    students = []
    # Expecting a csv of form: name,github
    with Reader(data_file, has_header=True) as rd:
        for row in rd:
            students.append(row)

    for week in namer.cycle_weeks():
        width = 25
        if args.display in ['lines', 'table']:
            print(f'Projects for {Fore.YELLOW}{namer.module_name}{week+1}{Style.RESET_ALL}:\n')
        if args.display == 'table':
            project_names = list(namer.cycle_names(week))
            # if there are 2 adiacent max length proj names, the column will touch
            # and be hard to copy paste.
            # still I'd rather leave it like this
            # and save that extra space to fit as much as possible on one row
            width = max(map(len, project_names))
            header_str = get_table_header_str(project_names, width)
            print(header_str)

        for student in students:
            if args.display == 'lines':
                print(f'{Fore.YELLOW}{student["name"]}{Style.RESET_ALL}:')

            project2repo = {prj:f'{prj}-{student["github"]}' for prj in namer.cycle_names(week)}
            student_repos_activity = process_batch(project2repo)

            # Dispaly them in the order of the initial dict keys
            student_repos_activity_strs = {}
            for project, activity in student_repos_activity.items():
                activity_str = get_activity_str(activity, width)
                if args.display == 'lines':  # print the project line directly
                    print(f'{project2repo[project]:<50}{activity_str}')
                elif args.display == 'table':  # gather the project activities to be printed on a single line
                    student_repos_activity_strs[project] = activity_str

            if args.display == 'lines':
                print()
            if args.display == 'table':
                row_str = get_table_row_str(student["name"], student["github"], student_repos_activity_strs)
                print(row_str)
        print()

    # Don't mind improper program exit - this will just let windows consoles in a messed up state
    # but windows users close consoles on sight so it's cheaper for the code complexity to leave that out
    colorama.deinit()