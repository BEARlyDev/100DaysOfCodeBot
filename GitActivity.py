#!/usr/bin/env python

import dataset
import dateparser
import requests


class GitActivity:

    db = None
    users = None
    github_activity = None

    def __init__(self):
        self.db = dataset.connect('sqlite:///todo.db')

        self.users = self.db['users']
        self.github_activity = self.db['github_activity']

    def update_leaderboard(self):
        for user in self.users:
            github_username = user['gitname']

            if github_username == '':
                continue

            github_username = github_username.lower()

            activity = self.github_activity.find_one(gitname=github_username, order_by='-id')
            yesterday = dateparser.parse('yesterday')

            if not activity or dateparser.parse(activity['updated']).date() != yesterday.date():
                save = self.save_activity(github_username)
                if save:
                    print('Updated info of %s' % github_username)
                elif save == False:
                    print('Couldn\'t get info of %s' % github_username)

    def save_activity(self, github_username):
        github_username = github_username.lower()

        r = requests.get('https://api.github.com/users/%s/events/public?client_id=ae8c70c7b22c2f1ba4c2&client_secret=a740e64e23809955c54425dd2815c06f1c6ad7a0' % github_username, timeout=15)
        result = r.json()

        if not result or type(result) != type([]):
            return False

        commits = 0

        for event in result:
            eventType = event['type']
            yesterday = dateparser.parse('yesterday').date()

            if eventType == 'PushEvent' and dateparser.parse(event['created_at']).date() == yesterday:
                commits += int(event['payload']['size'])

        if commits == 0:
            return None

        self.github_activity.insert({
            'gitname': github_username,
            'commits': commits,
            'updated': str(yesterday)
        })

        return True

    def get_total_commit_count(self, github_username):
        try:
            commits = 0

            for result in self.github_activity.find(gitname = github_username):
                commits += result['commits']

            return commits
        except:
            return 0

