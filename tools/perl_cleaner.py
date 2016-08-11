""" Perl cleaner. """

import os

from base import Task as BaseTask

tool_name = __name__

class Task(BaseTask):

    name = tool_name

    def perform(self):
        return os.system('perl-cleaner')
