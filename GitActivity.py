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
            username = user['username']

            activity = self.github_activity.find_one(username=username, order_by='-id')
            yesterday = dateparser.parse('yesterday')

            if not activity or dateparser.parse(activity['updated']).date() != yesterday.date():
                if user['gitname'] == '':
                    continue

                if self.save_activity(user['gitname']):
                    print('Updated info of %s.' % username)
                else:
                    print('Couldn\'t get info of %s.' % username)

    def save_activity(self, github_username):
        r = requests.get('https://api.github.com/users/%s/events/public' % github_username)
        result = r.json()

        if not result or type(result) != type([]):
            return False

        commits = 0

        for event in result:
            eventType = event['type']
            yesterday = dateparser.parse('yesterday').date()

            if eventType == 'PushEvent' and dateparser.parse(event['created_at']).date() == yesterday:
                commits += int(event['payload']['size'])

        if commits > 0:
            self.github_activity.insert({
                'gitname': github_username,
                'commits': commits,
                'updated': str(yesterday)
            })

        return True

g = GitActivity()
g.update_leaderboard()
