""" Portage distfiles clean. """

import os

from base import Task as BaseTask

tool_name = __name__

class Task(BaseTask):

    name = tool_name

    def perform(self):
        executable = self.env['%s_BIN' % tool_name.upper()]
        return os.system('%s --time-limit=2m' % executable)


def configure(conf):
    conf.env['%s_BIN' % tool_name.upper()] = \
            conf.find_program('eclean-dist')[0]
