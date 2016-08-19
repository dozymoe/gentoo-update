"""
Install kernels.

Options:

    * count     : integer, 3, number of kernel images to keep
    * preserved : list, [], kernel package atoms to preserve

"""

import os
import pexpect
import re
from base import Task as BaseTask, make_list
from shutil import copyfile, Error
from subprocess import check_output, CalledProcessError

tool_name = __name__

class BaseKernel(object):

    variant = None
    major = None
    minor = None
    micro = None
    extended = None
    version_regex = re.compile(r'(?P<major>\d+)\.(?P<minor>\d+)\.(?P<micro>\d+)(-r(?P<extended>\d+))?')

    def __init__(self, version_info):
        version = version_info.split(':')[1]
        match = re.search(self.version_regex, version)
        self.major = int(match.group('major'))
        self.minor = int(match.group('minor'))
        self.micro = int(match.group('micro'))
        if not match.group('extended') is None and len(match.group('extended')):
            self.extended = int(match.group('extended'))

    @property
    def weight(self):
        return (self.major, self.minor, self.micro or 0, self.extended or 0)

    @property
    def package_atom(self):
        return 'sys-kernel/' + self.package_atom_project_id

    @property
    def package_atom_project_id(self):
        result = '%s-%s.%s.%s' % (self.package_atom_project_name, self.major, self.minor, self.micro)
        if not self.extended is None:
            result = result + '-r' + str(self.extended)
        return result

    @property
    def package_atom_project_name(self):
        return '%s-sources' % self.variant

    @property
    def source_directory(self):
        result = '%s-%s.%s.%s-%s' % ('/usr/src/linux', self.major, self.minor, self.micro, self.variant)
        if not self.extended is None:
            result = result + '-r' + str(self.extended)
        return result

    @property
    def kernel_id(self):
        result = '%s.%s.%s-%s' % (self.major, self.minor, self.micro, self.variant)
        if not self.extended is None:
            result = result + '-r' + str(self.extended)
        return result

    def use_patch(self, patch_name):
        return False


class PfKernel(BaseKernel):

    variant = 'pf'
    version_regex = re.compile(r'(?P<major>\d+)\.(?P<minor>\d+)(_p(?P<extended>\d+))?')

    def __init__(self, version_info):
        version = version_info.split(':')[1]
        match = re.search(self.version_regex, version)
        self.major = int(match.group('major'))
        self.minor = int(match.group('minor'))
        self.micro = 0
        self.extended = int(match.group('extended'))

    @property
    def package_atom_project_id(self):
        return '%s-%s.%s_p%s' % (self.package_atom_project_name, self.major, self.minor, self.extended)

    @property
    def source_directory(self):
        return '%s-%s.%s_p%s-%s' % ('/usr/src/linux', self.major, self.minor, self.extended, self.variant)

    @property
    def kernel_id(self):
        return '%s.%s.%s-%s%s' % (self.major, self.minor, self.micro, self.variant, self.extended)

    def use_patch(self, patch_name):
        return False


class RaspberryPiKernel(BaseKernel):

    variant = 'raspi'
    version_regex = re.compile(r'(?P<major>\d+)\.(?P<minor>\d+)\.(?P<micro>\d+)(?P<extended>[\w-]*)')


class HardenedKernel(BaseKernel):
    variant = 'hardened'


class TuxOnIceKernel(BaseKernel):
    variant = 'tuxonice'


class GentooKernel(BaseKernel):
    variant = 'gentoo'


KERNEL_INFOS = {
    'sys-kernel/gentoo-sources': GentooKernel,
    'sys-kernel/hardened-sources': HardenedKernel,
    'sys-kernel/pf-sources': PfKernel,
    'sys-kernel/tuxonice-sources': TuxOnIceKernel,
}


def shell(command):
    ret = os.system(command)
    #print(command, ret)
    return ret == 0


class MultipleUplinkPatch(object):

    class Meta(object):
        routes_body_cache = None

    package = None

    def __init__(self, package):
        self.package = package

    @property
    def patch_filename(self):
        return os.path.join('/etc/portage/patches/sys-kernel',
                self.package.package_atom_project_id, 'multipath_routes.patch')

    @property
    def has_patch(self):
        if self.package.variant == 'hardened':
            # can't patch hardened source :(
            return True
        return os.path.lexists(self.patch_filename)

    def download(self):
        if self.has_patch:
            return
        if self.Meta.routes_body_cache is None:
            response = requests.get('http://ja.ssi.bg/#routes')
            if not response.ok:
                return
            self.Meta.routes_body_cache = response.text
        html = BeautifulSoup.BeautifulSoup(self.Meta.routes_body_cache)
        search_re = re.compile(r'^patch-(?P<major>\d+)\.(?P<minor>\d+)-ja\d*\.diff$')
        patch_url = None
        for anchor in html.findAll('a'):
            match = re.search(search_re, anchor.text)
            if match is None:
                continue
            if int(match.group('major')) > self.package.major:
                continue
            if int(match.group('minor')) > self.package.minor:
                continue
            attrs = {item[0]: item[1] for item in anchor.attrs}
            patch_url = urlparse.urljoin('http://ja.ssi.bg', attrs['href'])
            break
        if patch_url is None:
            return
        response = requests.get(patch_url)
        if not response.ok:
            return
        try:
            os.makedirs(os.path.dirname(self.patch_filename))
        except OSError as e:
            # directory already exists
            pass
        with open(self.patch_filename, 'w') as f:
            f.write(response.text.encode('utf8'))


class Task(BaseTask):

    name = tool_name
    max_images = None
    preserved_kernels = None

    def prepare(self):
        cfg = self.conf

        self.max_images = cfg.get('count', 3)

        self.preserved_kernels = []
        for package in make_list(cfg.get('preserved')):
            self.preserved_kernels.append(package)


    def perform(self):
        try:
            packages_ret = check_output('eix --installed --only-names sys-kernel/*-sources', shell=True).decode()
        except CalledProcessError as e:
            if e.returncode > 0:
                return 0
            else:
                return e.returncode

        packages = packages_ret.splitlines()
        self.bld.to_log('\nUpdating kernel packages...')
        if not shell('emerge -uN ' + ' '.join(packages)):
            self.bld.to_log('\nFailed to emerge kernels')
            return -1

        for package in packages:
            kernel_class = KERNEL_INFOS[package]
            installed_ret = check_output('qlist -ICS ' + package, shell=True).decode()
            installed_raw = [kernel_class(pkg.strip()) for pkg in installed_ret.splitlines()]

            installed_weighted = []
            # sort by versions
            for pkg in installed_raw:
                installed_weighted.append((pkg.weight, pkg.variant, pkg))
            installed_weighted.sort()

            # keep the last MAX_KERNEL_VERSIONS for each type
            for_keep = []
            kept = {}
            unique_versions = set()
            for weight, variant, pkg in reversed(installed_weighted):
                if variant not in kept:
                    kept[variant] = 0

                version_id = (variant, weight[0], weight[1])
                if version_id not in unique_versions:
                    unique_versions.add(version_id)
                    if kept[variant] < self.max_images:
                        kept[variant] += 1
                        for_keep.append(pkg)
                    else:
                        break

            for weight, variant, pkg in installed_weighted:
                config_path = os.path.join(pkg.source_directory, '.config')

                if os.path.lexists(config_path):
                    self.bld.to_log('\nBackup .config from %s...' % pkg.source_directory)
                    shell('cp %s /usr/src/kernel-%s.config' % (config_path, variant))
                else:
                    self.bld.to_log('\nRestore .config to %s...' % pkg.source_directory)
                    if not shell('cp /usr/src/kernel-%s.config %s' % (variant, config_path)):
                        self.bld.msg('/usr/src/kernel-%s.config' % variant, 'Not found')
                        return -1

                try:
                    for_keep_idx = for_keep.index(pkg)
                except ValueError:
                    for_keep_idx = -1

                # remove old packages
                if for_keep_idx == -1:
                    reserved = False

                    # check if kernel was reserved
                    for kernel_atom in self.preserved_kernels:
                        if pkg.package_atom.startswith(kernel_atom):
                            reserved = True
                            break

                    if reserved:
                        continue

                    self.bld.to_log('\nUninstall %s...' % pkg.package_atom)
                    shell('emerge -c =' + pkg.package_atom)

                    self.bld.to_log('\nCleanup /boot...')
                    shell('rm /boot/*%s*' % pkg.kernel_id)

                    self.bld.to_log('\nCleanup %s...' % pkg.source_directory)
                    shell('rm -rf %s' % pkg.source_directory)

                    modules_path = os.path.join('/lib/modules', pkg.kernel_id)
                    self.bld.to_log('\nCleanup %s...' % modules_path)
                    shell('rm -rf %s' % modules_path)

                else:
                    reinstall = False

                    if pkg.use_patch('MultipleUplink'):
                        multiple_uplink_patch = MultipleUplinkPatch(pkg)
                        if not multiple_uplink_patch.has_patch:
                            multiple_uplink_patch.download()
                            reinstall = True

                    if reinstall:
                        shell('emerge =' + pkg.package_atom)

                    self.bld.to_log('\nMake oldconfig in %s...' % pkg.source_directory)
                    child = pexpect.spawn('make -j1 -C %s silentoldconfig' % pkg.source_directory)
                    while child.isalive():
                        try:
                            child.expect([
                                r'\] \(NEW\)',
                                r'choice\[\d+-\d+\??\]: (?!\d+)'])
                            print(child.before.decode() + child.after.decode())
                            child.send('\n')
                        except pexpect.exceptions.EOF:
                            print(child.before.decode())
                        except pexpect.exceptions.TIMEOUT:
                            print(child.before.decode())
                    if child.exitstatus:
                        self.bld.msg('Configure kernel', 'Failed')
                        return -1

                    self.bld.to_log('\nMake in %s...' % pkg.source_directory)
                    if not shell('make -j8 -C %s' % pkg.source_directory):
                        self.bld.msg('Build kernel', 'Failed')
                        return -1

                    self.bld.to_log('\nMake install in %s...' % pkg.source_directory)
                    shell('make -C %s install' % pkg.source_directory)
                    shell('make -C %s modules_install' % pkg.source_directory)

                    if for_keep_idx > 0:
                        boot_symlink = os.path.join('/boot', '%s.%s' % (variant, for_keep_idx))
                    else:
                        boot_symlink = os.path.join('/boot', variant)
                    self.bld.to_log('\nCreate symlink %s...' % boot_symlink)
                    shell('rm ' + boot_symlink)
                    shell('ln -s vmlinuz-%s %s' % (pkg.kernel_id, boot_symlink))

                    if for_keep_idx == 0:
                        src_symlink = os.path.join('/usr/src', variant)
                        self.bld.to_log('\nCreate symlink %s...' % src_symlink)
                        shell('rm ' + src_symlink)
                        shell('ln -s %s %s' % (pkg.source_directory, src_symlink))
        return 0
