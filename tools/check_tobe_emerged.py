"""
Check if package was going to be upgraded/emerged.

Options:

    * name_regex : str, None, package atom

Requirements:

    * eix

"""

import os
from base import Task as BaseTask, make_list
from re import search
from subprocess import check_output
from time import time

tool_name = __name__

class Task(BaseTask):

    name = tool_name
    atom = None

    def prepare(self):
        cfg = self.conf
        self.args = ['-#', '-u']

        self.atom = cfg['name_regex']


    def perform(self):
        if len(self.file_out) != 1:
            self.bld.fatal('%s can only have one output' % tool_name.capitalize())

        executable = self.env['%s_BIN' % tool_name.upper()]
        os.environ['EIX_LIMIT'] = '0'
        ret = check_output(
            '{exe} {arg}'.format(
                exe=executable,
                arg=' '.join(self.args)),
            shell=True,
            universal_newlines=True)

        filename = self.file_out[0]
        try:
            os.makedirs(os.path.dirname(filename))
        except OSError:
            pass

        if search(self.atom, ret) or not os.path.exists(filename):
            with open(filename, 'w') as f:
                f.write(str(time()))


def configure(conf):
    conf.env['%s_BIN' % tool_name.upper()] = conf.find_program('eix')[0]
