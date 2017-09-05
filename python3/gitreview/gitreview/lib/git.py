#!/usr/bin/env python
''' Module for obtaining information from a git repository
'''
import logging
import subprocess
import shlex
import re

LOGGER = logging.getLogger()

class StashError(Exception):
    ''' Custom error for subprocess failures
    '''
    def __init__(self, *args, **kwargs):
        ''' Initialization method
        '''
        Exception.__init__(self, *args, **kwargs)

def run_proc(cmd):
    ''' Abstract out the running of subprocesses, convert output to utf-8
        string, and return it. Error when errors are returned.
    '''
    proc = subprocess.Popen(shlex.split(cmd),
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE)
    LOGGER.info('Executing "%s"', cmd)
    out, err = proc.communicate()
    if err:
        raise SubprocessError(err.decode('utf-8'))
    return out.strip().decode('utf-8')

class SubprocessError(Exception):
    ''' Custom error for subprocess failures
    '''
    def __init__(self, *args, **kwargs):
        ''' Initialization method
        '''
        Exception.__init__(self, *args, **kwargs)

class Git(object):
    ''' Abstraction of a git repository's information
    '''
    def __init__(self, target='master'):
        self._description = ''
        self._slug = ''
        self._key = ''
        self._target = target
        self._branch = ''
        self._address = ''
    @property
    def target(self):
        ''' Propertize the target
        '''
        return self._target
    @property
    def branch(self):
        ''' Propertize the branch
        '''
        if not self._branch:
            branch_cmd = 'git rev-parse --abbrev-ref HEAD'
            LOGGER.info('Obtaining branch name')
            self._branch = run_proc(branch_cmd)
        return self._branch
    @property
    def description(self):
        ''' Propertize the description
        '''
        if not self._description:
            description_cmd = ('git log --reverse --format=%s {target}..{branch}'
                               .format(target=self._target, branch=self.branch))
            LOGGER.info('Obtaining description name')
            self._description = run_proc(description_cmd)
        return self._description
    @property
    def key(self):
        ''' Propertize the key
        '''
        if not self._key:
            self._remoteinfo()
        return self._key
    @property
    def slug(self):
        ''' Propertize the slug
        '''
        if not self._slug:
            self._remoteinfo()
        return self._slug
    @property
    def address(self):
        ''' Propertize the remote address
        '''
        if not self._address:
            self._remoteinfo()
        return self._address
    def _remoteinfo(self):
        remote_cmd = 'git remote -v'
        LOGGER.info('Obtaining remote information')
        remotes = run_proc(remote_cmd).split('\n')
        try:
            origin = [i for i in remotes if 'origin' in i][0]
        except IndexError:
            msg = ('Cannot find a git remote matching {remote}.'
                   .format(remote='origin'))
            raise GitRemoteNotFoundError(msg)
        LOGGER.info(origin)
        reg = re.compile(r'\/([\w@\.:-]+)\/([~\w-]+)\/([\w-]+).git', re.I)
        result = re.search(reg, origin)
        self._address = result.groups()[0].split('@')[-1].split(':')[0]
        self._key = result.groups()[1]
        self._slug = result.groups()[2]
    def push(self):
        LOGGER.info('Pushing branch to git')
        try:
            _ = run_proc('git push origin {branch}'.format(branch=self.branch))
        except SubprocessError as err:
            errstring = str(err)
            reraise = ('View pull request for' not in errstring and
                       'Create pull request' not in errstring and
                       'Everything up-to-date' not in errstring)
            if not reraise:
                print(str(err))
            else:
                raise
