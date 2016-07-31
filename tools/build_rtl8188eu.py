""" Build kernel module for rtl8188eu. """

import os

from base import Task as BaseTask

tool_name = __name__

class Task(BaseTask):

    name = tool_name

    def perform(self):
        cwd = os.path.realpath(os.curdir)
        os.chdir('/usr/src/local/rtl8188eu')
        ret = os.system('make && make install')
        os.chdir(cwd)
        return ret
