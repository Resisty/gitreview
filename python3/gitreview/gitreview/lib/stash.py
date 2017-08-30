#!/usr/bin/env python
''' This module abstracts a minimal section of the stash REST api
'''
import logging
import requests
import yaml

APIFMT = '''https://{addr}/rest/api/1.0/projects/{key}/\
repos/{slug}/pull-requests'''
LOGGER = logging.getLogger()
REQJSON = {'title':'',
           'description':'',
           'state':'OPEN',
           'open':True,
           'closed':False,
           'fromRef': {'id': 'refs/heads/{branch}',
                       'repository': {'slug': '',
                                      'name':None,
                                      'project':{'key': ''}
                                     }
                      },
           'toRef': {'id': 'refs/heads/master',
                     'repository': {'slug': '',
                                    'name': None,
                                    'project': {'key': ''
                                               }
                                   }
                    },
           'locked': False}

def getcreds(func):
    ''' Decorator for getting stash credentials when needed but not every time.
    '''
    def wrapper(self, *args, **kwargs):
        ''' The wrapper used by the decorator.
        '''
        #pylint: disable=protected-access
        if not self._user and not self._password:
            with open(self._credsfile) as creds:
                userdata = yaml.load(creds.read())
                self._user = userdata['stashuser']
                self._password = userdata['stashpass']
                self._proxy = userdata.get('proxy', '')
                self._proxyuser = userdata.get('proxyuser', self._user)
                self._proxypass = userdata.get('proxypass', self._password)
        func(self, *args, **kwargs)
    return wrapper

class StashError(Exception):
    ''' Custom error for subprocess failures
    '''
    def __init__(self, *args, **kwargs):
        ''' Initialization method
        '''
        Exception.__init__(self, *args, **kwargs)

class Stash(object):
    ''' Stash abstracts the REST call of creating a pull request
    '''
    def __init__(self, credentials):
        self._credsfile = credentials
        self._user = ''
        self._password = ''
        self._proxy = ''
        self._proxyuser = ''
        self._proxypass = ''
    @getcreds
    def submit(self, address, title, description, branch, key, slug):
        ''' Do the actual work:
                Get git information, assemble it, make an HTTP request
        '''
        REQJSON['title'] = title
        REQJSON['description'] = description
        REQJSON['fromRef']['id'] = (REQJSON['fromRef']['id']
                                    .format(branch=branch))
        REQJSON['fromRef']['repository']['slug'] = slug
        REQJSON['fromRef']['repository']['project']['key'] = key
        REQJSON['toRef']['repository']['slug'] = slug
        REQJSON['toRef']['repository']['project']['key'] = key
        stashaddr = APIFMT.format(addr=address,
                                  key=key,
                                  slug=slug)
        request = requests.post(stashaddr,
                                json=REQJSON,
                                proxies=self._mkproxy(),
                                auth=(self._user, self._password))
    def _mkproxy(self):
        ''' Assemble a proxy if configured
        '''
        if self._proxy:
            proxy = {'https': ('https://{user}:{password}@{proxy}'
                               .format(user=self._user,
                                       password=self._password,
                                       proxy=self._proxy))}
            return proxy
        return {}
