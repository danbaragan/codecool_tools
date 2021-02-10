#!/usr/bin/env python

from dotenv import load_dotenv
load_dotenv()
import argparse
import concurrent.futures
import os
from pathlib import Path
import sys

from colorama import Fore, Style
from agithub.GitHub import GitHub

from lib.project_namer import namer_class_factory
from lib.data_printer import printer_factory
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
        # we bail out from a thread on behalf of the entire process!
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
    parser.add_argument('-d', '--display', choices=['lines', 'table', 'csv'], default='table',
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

    namer = namer_class_factory(args.module[0])(args.type, args.weeks)

    students = []
    # Expecting a csv of form: name,github
    with Reader(data_file, has_header=True) as rd:
        for row in rd:
            students.append(row)

    printer = printer_factory(args.display, __file__)
    with printer as printer:
        for week in namer.cycle_weeks():
            printer.module_line(namer.module_name, week)

            project_names = list(namer.cycle_names(week))
            printer.inter_header(project_names)

            for student in students:
                printer.student_cells(student["name"], student["github"])

                project2repo = {prj:f'{prj}-{student["github"]}' for prj in project_names}
                student_repos_activity = process_batch(project2repo)

                # Display them in the order of the initial dict keys
                for project, activity in student_repos_activity.items():
                    printer.activity_cells(project2repo[project], activity)

                printer.flush_row()
            print()
