"""
Build kernel module for rtl8188eu.

Uses https://github.com/dozymoe/rtl8188eu which adds support for
CUSTOM_KERNEL_VERSION environment variable.
"""

import os

from subprocess import check_output, CalledProcessError
from tempfile import gettempdir

from base import Task as BaseTask
from tools.emerge_kernel import KERNEL_INFOS

SOURCE_DIR = '/usr/src/local/rtl8188eu'

tool_name = __name__

class Task(BaseTask):

    name = tool_name

    def perform(self):
        try:
            packages_ret = check_output(
                    'eix --installed --only-names sys-kernel/*-sources', shell=True,
                    universal_newlines=True)

        except CalledProcessError as e:
            if e.returncode > 0:
                return 0
            else:
                return e.returncode

        for package in packages_ret.splitlines():
            kernel_class = KERNEL_INFOS[package]

            installed_ret = check_output(
                    'qlist --installed --slots --nocolor %s' % package, shell=True,
                    universal_newlines=True)

            installed = [kernel_class(pkg.strip()) for pkg in \
                    installed_ret.splitlines()]

            for kernel in installed:
                builddir = os.path.join(gettempdir(), 'rtl8188eu', kernel.kernel_id)
                if not os.path.exists(builddir):
                    os.makedirs(builddir)

                os.system('cp -a %s %s' % (os.path.join(SOURCE_DIR, '*'), builddir))

                os.environ['CUSTOM_KERNEL_VERSION'] = kernel.kernel_id

                ret = os.system('make -C %s clean' % builddir)
                if ret == 0:
                    ret = os.system('make -C %s' % builddir)
                if ret == 0:
                    ret = os.system('make -C %s install' % builddir)
                if ret:
                    return ret

                os.system('rm -r %s' % builddir)

        return 0
