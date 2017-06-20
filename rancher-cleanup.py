#!/usr/bin/env python
import datetime
import requests
import json
import re
import schedule
import time
import os

def get_repo_stub_from_desc(desc):
    # PR-176 (feature/branch) github/nhsuk/register-with-a-gp-beta-web
    match = re.search('github\/(\S+)$', desc)
    if match:
        return match.group(1)
    else:
        return None


def get_pr_id_from_desc(desc):
    # PR-176 (feature/branch) github/nhsuk/register-with-a-gp-beta-web
    match = re.search('PR-(\d+)', desc)
    if match:
        return match.group(1)
    else:
        return None


def rm_rancher_stack(remove_url):
    remove_request = requests.post(
      remove_url,
      auth=(RANCHER_ACCESS_KEY, RANCHER_SECRET_KEY)
    )

def clean_stack(stackdata):
    i = stackdata

    if "-pr-" not in i['name']:
        return

    name = i['name']
    description = i['description']

    if not description:
        return

    pr_id = get_pr_id_from_desc(description)
    repo  = get_repo_stub_from_desc(description)

    if (pr_id == None) or (repo == None):
        print("description doesn't look right...")
        return
    else:
        print("Description looks right: ")
        print("\trepo="+repo)
        print("\tpr_id="+pr_id)

    github_data = requests.get(
      'https://api.github.com/repos/' + repo + '/pulls/' + pr_id,
      auth=(GITHUB_USER, GITHUB_ACCESS_TOKEN)
    ).json()

    # delete stack if PR is closed in gitlab
    if github_data['state'] == 'closed':
        print("PR is closed, so deleting stack")
        delete_stack(i['actions']['remove'])

    # delete stack if it's over 7 days old
    now = datetime.datetime.now()
    week_ago = now - datetime.timedelta(days=7)
    stack_creation = datetime.datetime.fromtimestamp((i['createdTS']/1000))
    if stack_creation < week_ago:
        print("stack was created over 1 week ago, removing")
        delete_stack(i['actions']['remove'])


def clean_all_stacks():
    all_stacks = requests.get(
                 'https://' + RANCHER_SERVER + '/v2-beta/stacks?limit=200',
                 auth=(RANCHER_ACCESS_KEY, RANCHER_SECRET_KEY)
                 ).json()

    for i in all_stacks['data']:
        clean_stack(i)


RANCHER_SERVER = os.getenv('RANCHER_SERVER')
RANCHER_ACCESS_KEY = os.getenv('RANCHER_ACCESS_KEY')
RANCHER_SECRET_KEY = os.getenv('RANCHER_SECRET_KEY')
GITHUB_USER = os.getenv('GITHUB_USER')
GITHUB_ACCESS_TOKEN = os.getenv('GITHUB_ACCESS_TOKEN')
SCHEDULE_RUN_EVERY = os.getenv('SCHEDULE_RUN_EVERY')

schedule.every(SCHEDULE_RUN_EVERY).minutes.do(clean_all_stacks)
while True:
    schedule.run_pending()
    time.sleep(1)
