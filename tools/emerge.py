"""
Install/upgrade gentoo sytem packages.

Options:

    * items         : list, [],    packages to install
    * deep          : bool, False, check dependencies
    * fetch         : bool, False, fetch sources only
    * new_use       : bool, False, update if use flags changed
    * update        : bool, False, update packages
    * depclean      : bool, False, prune packages
    * ignore_errors : bool, False, ignore errors
    * keep_going    : bool, None,  keep going if some package failed to build

Requirements:

    * portage

"""

import os
from base import Task as BaseTask, make_list

tool_name = __name__

class Task(BaseTask):

    name = tool_name
    ignore_errors = False

    def prepare(self):
        cfg = self.conf

        if cfg.get('fetch'):
            self.args.append('--fetchonly')

        if cfg.get('update'):
            self.args.append('--update')

        if cfg.get('deep'):
            self.args.append('--deep')

        if cfg.get('new_use'):
            self.args.append('--newuse')

        if cfg.get('depclean'):
            self.args.append('--depclean')

        if cfg.get('keep_going'):
            self.args.append('--keep-going')
            self.args.append('y')

        for package in make_list(cfg.get('items')):
            self.args.append(package)

        self.ignore_errors = cfg.get('ignore_errors', False)


    def perform(self):
        if 'PYTHONPATH' in os.environ:
            del os.environ['PYTHONPATH']

        executable = self.env['%s_BIN' % tool_name.upper()]
        ret = os.system(
            '{exe} {arg}'.format(
            exe=executable,
            arg=' '.join(self.args),
        ))
        if self.ignore_errors or ret >= 0:
            return 0
        else:
            return ret


def configure(conf):
    conf.env['%s_BIN' % tool_name.upper()] = conf.find_program('emerge')[0]
