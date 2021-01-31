#!/usr/bin/env python

from dotenv import load_dotenv
load_dotenv()
import argparse
import os
from pprint import pprint as pp

from colorama import Fore, Back, Style
from agithub.GitHub import GitHub

from lib.project_namer import PgProjectNamer, print_projects
from lib.data_reader import Reader



hub_client = GitHub(token=os.getenv('TOKEN'))

if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog='si_work.py',
    description=f"""Show what work in terms of commits sudets did during their SI week
    """,
    epilog="You should have ?.csv file with... ")

    parser.add_argument('-t', '--type', choices=['si', 'tw'], default='si',
        help='week type; si or tw; default si')
    parser.add_argument('week', type=int, nargs='?', choices=[1, 2, 3, 4, 5, 6], default=None,
        help='Week number to show; All if empty; default empty')

    args = parser.parse_args()

    namer = PgProjectNamer(args.type, args.week)

    students = []
    # Expecting a csv of form: name,github
    with Reader('data/students.csv') as rd:
        for row in rd:
            students.append(row)

    for week in namer.cycle_weeks():
        print(f'Projects for {Fore.YELLOW}{namer.module_name}{week+1}{Style.RESET_ALL}:')
        for student in students:
            print(f'{Fore.YELLOW}{student["name"]}{Style.RESET_ALL}:')
            for prj in namer.cycle_names(week):
                project = f'{prj}-{student["github"]}'
                # https://docs.github.com/en/rest/reference/repos#get-a-repository
                status, resp = hub_client.repos.CodecoolGlobal[project].commits.get()

                activity = 'err'
                if status == 404:
                    activity = f'{Fore.RED}repo not started{Style.RESET_ALL}'
                elif status == 200:
                    commits_no = len(resp)
                    if commits_no <= 1:
                        activity = f'{Fore.RED}{commits_no}{Style.RESET_ALL}'
                    else:
                        activity = f'{Fore.GREEN}{commits_no}{Style.RESET_ALL}'
                
                print(f'{project}: {activity}')
        print()
