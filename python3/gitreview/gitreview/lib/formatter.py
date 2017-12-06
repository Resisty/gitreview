#!/usr/bin/env python
# -*- coding: utf-8 -*-
''' Module for generating formatted Pull Request descriptions/information
'''

import os
import logging
import yaml

from gitreview.lib.git import run_proc

LOGGER = logging.getLogger()
GITROOT = run_proc('git rev-parse --show-toplevel')
YAMLFILE = os.path.join(GITROOT, 'review.yaml')

YAML_TEMPLATE = '''---
reqs: ''
context: ''
validation: ''
testing: ''
additional: ''
tickets: ''
gif: ''
bool_coverage: false
bool_infracode: false
bool_configbooks: false
bool_docs: false
bool_regresssion: false
'''

def provide(path):
    ''' Produce a yaml file for the user to use in future PRs and replace
        relevant data.

        Positional Arguments:
            path -- Path at which to create the format data yaml file
    '''
    LOGGER.info('Opening %s for writing format data yaml template.', path)
    with open(path, 'w') as fptr:
        fptr.write(YAML_TEMPLATE)

FORMAT = '''### What does this PR do?

#### Requirements
{reqs}

#### Background Context
{context}

### Validation
{validation}
#### Manual Testing Steps
{testing}

### Additional Information
{additional}

#### Associated Tickets
{tickets}

#### Screenshots (if appropriate)

#### What gif best describes this PR or how it makes you feel?
{gif}
#### Definition of Done:
- [{bool_coverage}] Appropriate test coverage (unit tests, serverspec, etc...) completed
- [{bool_infracode}] Any required infrastructure has been codified
- [{bool_configbooks}] Cookbook/playbook has been updated with sane configuration
- [{bool_docs}] Documentation for service/tool has been provided or updated
- [{bool_regresssion}] Does this PR require a regression test? All fixes require a regression
  test.'''

def read(func):
    ''' Decorator for reading format data from yaml file once or when needed.
    '''
    def wrapper(self, *args, **kwargs):
        ''' The wrapper used by the decorator
        '''
        #pylint: disable=protected-access
        if not self._data or not self._do_read:
            try:
                with open(self._file) as ymlfile:
                    self._data = yaml.load(ymlfile.read())
            except IOError:
                self._data = {}
                self._do_read = False
        return func(self, *args, **kwargs)
    return wrapper

class Formatter(object):
    ''' Class representing the format of a Pull Request
        Provides a structured string to use as the description in the Stash API
        request. Pulls information from a yaml file, if it exists.
    '''
    def __init__(self, yamlfile=YAMLFILE):
        ''' Initialization method.

            Keyword Arguments:
                yamlfile -- Location of yaml file containing PR formatting data
        '''
        self._file = yamlfile
        self._do_read = True
        self._data = {}
    @read
    def set_tickets(self, tickets):
        ''' Allow Git data to provide related JIRA tickets, e.g. from branch
            name like feature/PROJECT-0001

            Positional Arguments:
                tickets -- string of ticket identifier(s)
        '''
        if self._data and 'tickets' in self._data and not self._data['tickets']:
            self._data['tickets'] = tickets
    @read
    def generate(self):
        ''' Produce a formatted string from available data, if it exists.
            Otherwise return None
        '''
        if not self._data:
            return None
        try:
            self._data.update({i: '✔️' if j else ' '
                               for i, j in self._data.items()
                               if i.startswith('bool')})
            fmt = FORMAT.format(**self._data)
            LOGGER.info('Returning fmt as "%s"', fmt)
            return fmt
        except KeyError as err:
            LOGGER.error('Data from review format yaml file missing field: \
"%s"', str(err))
            return None
