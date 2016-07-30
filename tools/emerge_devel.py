""" Emerge devel tools. """

import os

from base import Task as BaseTask

tool_name = __name__

class Task(BaseTask):

    name = tool_name

    def perform(self):
        binutils_ret = os.system('emerge -uN sys-devel/binutils')
        if binutils_ret:
            binutils_ret = os.system('emerge -uN --nodeps sys-devel/binutils')

        gcc_ret = os.system('emerge -uN sys-devel/gcc')
        return binutils_ret | gcc_ret
