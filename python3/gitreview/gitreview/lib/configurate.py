#!/usr/bin/env python
''' This module provides an abstraction for the configuration file for
    gitreview, defaulting to ~/.stashcreds.yaml
'''

import os
import getpass
import yaml

DEFAULTPATH = os.path.expanduser('~/.stashcreds.yaml')

def prompt():
    user = input('Stash username: ')
    password = getpass.getpass('Stash password: ')
    do_proxy = input('Do you use a proxy? y/n: ')
    proxy, proxyuser, proxypass = None, None, None
    if do_proxy in ['y', 'Y']:
        proxy = input('Proxy (format 127.0.0.1:9000): ')
        proxyuserpass = input('Is your proxy user/pass separate from Stash? \
y/n: ')
        if proxyuserpass in ['y', 'Y']:
            proxyuser = input('Proxy user: ')
            proxypass = getpass.getpass('Proxy password: ')
    path = input('Where would you like to save this config file? (default \
%s): ' % DEFAULTPATH) or DEFAULTPATH
    do_reviewers = input('Do you want to save default reviewers? y/n: ')
    if do_reviewers in ['y', 'Y']:
        reviewers = input('Enter reviewer usernames separated by spaces \
(user1 user2 ...): ')
        reviewers = reviewers.split(' ')
    cfg = Config(user,
                 password,
                 proxy=proxy,
                 proxyuser=proxyuser,
                 proxypass=proxypass,
                 reviewers=reviewers,
                 path=path)
    cfg.write()

class Config(object):
    ''' Abstraction of the credentials/config file
    '''
    def __init__(self,
                 user,
                 password,
                 proxy=None,
                 proxyuser=None,
                 proxypass=None,
                 reviewers=None,
                 path=DEFAULTPATH):
        self._user = user
        self._password = password
        self._proxy = proxy
        self._proxyuser = proxyuser or self._user
        self._proxypass = proxypass or self._password
        self._reviewers = reviewers
        self._path = path
    def write(self):
        with open(self._path, 'w') as writer:
            data = {'stashuser': self._user,
                    'stashpass': self._password}
            if self._proxy:
                data['proxy'] = self._proxy
                data['proxyuser'] = self._proxyuser
                data['proxypass'] = self._proxypass
            if self._reviewers:
                data['reviewers'] = self._reviewers
            writer.write(yaml.dump(data, default_flow_style=False))
