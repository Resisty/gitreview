#!/usr/bin/env python
''' This module is serves as the definition and entrypoint for quick git pull
    requests in Python at AWS Elemental. It is heavily customized because we use a
    proxy.
'''

import os
import shlex
import subprocess
import argparse
import re
import logging
import requests
import yaml
import gitreview.lib.git
import gitreview.lib.stash
import gitreview.lib.configurate
FORMAT = """[%(asctime)s] '%(message)s'"""
logging.basicConfig(format=FORMAT)
LOGGER = logging.getLogger()

def do_review(args):
    ''' Defaults function, called by argparse to create a review
    '''
    if args.configure:
        gitreview.lib.configurate.prompt()
    else:
        gitinfo = gitreview.lib.git.Git(target=args.target_branch)
        gitinfo.push()
        stash = gitreview.lib.stash.Stash(args.credentials)
        stash.submit(gitinfo.address,
                     gitinfo.branch,
                     gitinfo.description,
                     gitinfo.branch,
                     gitinfo.target,
                     gitinfo.key,
                     gitinfo.slug)

def gitmain():
    ''' Main function invoked at runtime
    '''
    parser = argparse.ArgumentParser('Parse arguments')
    parser.add_argument('--configure',
                        help='Set up your credentials/configuration file.',
                        action='store_true',
                        default=False)
    parser.add_argument('-t', '--target_branch',
                        help='Which git branch to target with the PR',
                        default='master')
    parser.add_argument('-c', '--credentials',
                        help='Path to stash credentials.',
                        default=gitreview.lib.configurate.DEFAULTPATH)
    parser.add_argument("-v", '--verbose',
                        help="Verbose",
                        action='count',
                        default=0)
    parser.set_defaults(func=do_review)
    args = parser.parse_args()
    levels = [logging.WARN, logging.INFO, logging.DEBUG]
    level = levels[min(len(levels)-1, args.verbose)]
    LOGGER.setLevel(level)
    args.func(args)

if __name__ == '__main__':
    gitmain()
