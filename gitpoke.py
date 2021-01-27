#!/usr/bin/env python

from dotenv import load_dotenv
load_dotenv()

import os
from github import Github
from pprint import pprint as pp

hub_client = Github(os.getenv('TOKEN'))

repo = hub_client.get_repo('CodecoolGlobal/agile-workshop-light')
pp(repo)
