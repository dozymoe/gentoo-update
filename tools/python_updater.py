""" Python updater. """

import os

from base import Task as BaseTask

tool_name = __name__

class Task(BaseTask):

    name = tool_name

    def perform(self):
        executable = self.env['%s_BIN' % tool_name.upper()]
        return os.system(executable)


def configure(conf):
    conf.env['%s_BIN' % tool_name.upper()] = \
            conf.find_program('python-updater')[0]
