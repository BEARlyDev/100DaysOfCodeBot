#!/usr/bin/env python

import dataset
import requests

db = dataset.connect('sqlite:///todo.db')

users = db['users']
github_activity = db['github_activity']
