#!/usr/bin/env python
''' This module abstracts a minimal section of the stash REST api
'''
import logging
import requests
import yaml

APIFMT = '''https://{addr}/rest/api/1.0/projects/{key}/\
repos/{slug}/pull-requests'''
LOGGER = logging.getLogger()
REVIEWEXC = 'com.atlassian.bitbucket.pull.InvalidPullRequestReviewersException'
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
           'toRef': {'id': 'refs/heads/{target}',
                     'repository': {'slug': '',
                                    'name': None,
                                    'project': {'key': ''
                                               }
                                   }
                    },
           'locked': False,
           'reviewers': []}

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
                self._reviewers = userdata.get('reviewers', [])
        func(self, *args, **kwargs)
    return wrapper

def reviewer_problem_maybe(response_json):
    errors = response_json.get('errors', [])
    for error in errors:
        if error['exceptionName'] == REVIEWEXC:
            return True
    return False

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
        self._reviewers = []
    @getcreds
    def submit(self, address, title, description, branch, target, key, slug):
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
        REQJSON['toRef']['id'] = (REQJSON['toRef']['id']
                                  .format(target=target))
        REQJSON['reviewers'] = [{'user':{'name': reviewer}}
                                for reviewer in self._reviewers]
        stashaddr = APIFMT.format(addr=address,
                                  key=key,
                                  slug=slug)
        request = requests.post(stashaddr,
                                json=REQJSON,
                                proxies=self._mkproxy(),
                                auth=(self._user, self._password))
        LOGGER.info('HTTP response code: %s', request.status_code)
        LOGGER.info('Request response: "%s"', request.text)
        if (request.status_code >= 400 and
            reviewer_problem_maybe(request.json())):
                self._reviewers = []
                self.submit(address, title, description, branch, target, key, slug)
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
