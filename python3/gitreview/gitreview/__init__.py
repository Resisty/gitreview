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
import gitreview.lib.formatter
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
        prformat = gitreview.lib.formatter.Formatter(args.review_format_data)
        prformat.set_tickets(gitinfo.branch)
        description = prformat.generate()
        description = description or gitinfo.description
        stash.submit(gitinfo.address,
                     gitinfo.branch,
                     description,
                     gitinfo.branch,
                     gitinfo.target,
                     gitinfo.key,
                     gitinfo.slug)

def search_default_branch():
    ''' Try to establish the default branch from the git project if we're in
        one
    '''
    try:
        return gitreview.lib.git.Git.default_branch()
    except gitreview.lib.git.SubprocessError:
        #Not in a git project?
        return 'master'

def gitprovide_format():
    ''' Function to create yaml data file for PR formats
    '''
    parser = argparse.ArgumentParser('Parse arguments')
    parser.add_argument('-f', '--file',
                        help='Path to create yaml data file for review \
formats.',
                        default=gitreview.lib.formatter.YAMLFILE)
    parser.add_argument("-v", '--verbose',
                        help="Verbose",
                        action='count',
                        default=0)
    args = parser.parse_args()
    levels = [logging.WARN, logging.INFO, logging.DEBUG]
    level = levels[min(len(levels)-1, args.verbose)]
    LOGGER.setLevel(level)
    gitreview.lib.formatter.provide(args.file)

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
                        default=search_default_branch())
    parser.add_argument('-c', '--credentials',
                        help='Path to stash credentials.',
                        default=gitreview.lib.configurate.DEFAULTPATH)
    parser.add_argument('-f', '--review_format_data',
                        help='Path to review format yaml data.',
                        default=gitreview.lib.formatter.YAMLFILE)
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
