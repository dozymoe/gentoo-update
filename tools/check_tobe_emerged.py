"""
Check if package was going to be upgraded/emerged.

Options:

    * name : str, None, package atom

Requirements:

    * eix

"""

import os
from base import Task as BaseTask, make_list
from time import time

tool_name = __name__

class Task(BaseTask):

    name = tool_name

    def prepare(self):
        cfg = self.conf
        self.args = ['--only-names', '--upgrade+']
        self.args.append(cfg['name'])


    def perform(self):
        if len(self.file_out) != 1:
            self.bld.fatal('%s can only have one output' % tool_name.capitalize())

        executable = self.env['%s_BIN' % tool_name.upper()]
        ret = os.system(
            '{exe} {arg}'.format(
            exe=executable,
            arg=' '.join(self.args)
        ))

        if ret == 0 or not os.path.exists(filename):
            with open(filename, 'w') as f:
                f.write(str(time()))


def configure(conf):
    conf.env['%s_BIN' % tool_name.upper()] = conf.find_program('eix')[0]
