# Mentor automation scripts
These scripts are ment to automate interaction with github as a mentor in order to get info or setup workshop boilerplates

## Requirements
- python 3 (3.9 was used)
- pip install requirements.txt
- github [token](https://github.com/settings/tokens) to put in .env file
- rename the needed templates inside data/ folder

## Gtihub Token

You need a token with at least the following:
- workflow (will include everything in repo)
- admin:org:read:org

## Usage

Generally, ./<script.py> -h is our friend.

So far:
- ./si_work.py module [week_number] - display the number of commits for each student si project in certain week.
