#!/usr/bin/env python
'''Wrapper script that manages multiple installed projects/tools'''

import os
import shlex
from argh import add_commands, dispatch
from argparse import ArgumentParser
from json import load as json_load

ROOT_DIR = os.path.realpath(os.path.dirname(__file__))

commands = []
env = {}


def prepare():
    os.environ['PACKAGE_ROOT_DIR'] = ROOT_DIR

    # setup virtualenv
    os.environ['PATH'] = ':'.join([
        os.path.join(ROOT_DIR, '.virtualenv', 'bin'),
        os.environ['PATH'],
    ])
    os.environ['PYTHONPATH'] = os.path.join(ROOT_DIR, 'python_modules')


def build(*args):
    prepare()

    if len(args) == 1:
        args = shlex.split(args[0])

    # my build tool is broken ;(
    # quick fix: force clean for each build
    binargs = ['waf', 'clean', 'build'] + list(args)
    os.execvp(binargs[0], binargs)
commands.append(build)


def waf(*args):
    prepare()

    if len(args) == 1:
        args = shlex.split(args[0])

    binargs = ['waf'] + list(args)
    os.execvp(binargs[0], binargs)
commands.append(waf)


def pip(*args):
    prepare()

    if len(args) == 1:
        args = shlex.split(args[0])

    binargs = ['pip'] + list(args)
    os.execvp(binargs[0], binargs)
commands.append(pip)


if __name__ == '__main__':
    parser = ArgumentParser()
    add_commands(parser, commands)
    dispatch(parser)
