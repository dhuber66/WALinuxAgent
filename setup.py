<<<<<<< HEAD
#!/usr/bin/python
#
# Windows Azure Linux Agent setup.py
=======
#!/usr/bin/env python
#
# Microsoft Azure Linux Agent setup.py
>>>>>>> 6883b02ac1cfe31db7d9797dde4504fb471f9954
#
# Copyright 2013 Microsoft Corporation
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
<<<<<<< HEAD
import glob
import os
import sys
import platform
import setuptools
from setuptools.command.install import install

from distutils.errors import DistutilsArgError

def getDistro():
    """
    Try to figure out the distribution we are running on
    """
    distro = platform.linux_distribution()[0].lower()
    # Manipulate the distribution to meet our needs we treat
    # Fedora, RHEL, and CentOS the same
    # openSUSE and SLE the same
    if distro.find('suse') != -1:
        distro = 'suse'
    if (distro.find('fedora') != -1
    or distro.find('red hat') != -1
    or distro.find('centos') != -1):
        distro = 'redhat'

    return distro
    

class InstallData(install):
    user_options = install.user_options + [
        # This will magically show up in member variable 'init_system'
        ('init-system=', None, 'init system to configure [default: sysV]'),
        ('lnx-distro=', None, 'target Linux distribution'),
    ]

    def initialize_options(self):
        install.initialize_options(self)
        self.init_system = 'sysV'
        self.lnx_distro = None

    def finalize_options(self):
        install.finalize_options(self)
        if not self.lnx_distro:
            self.lnx_distro = getDistro()
        if self.init_system not in ['sysV', 'systemd', 'upstart']:
            print 'Do not know how to handle %s init system' %self.init_system
            sys.exit(1)
        if self.init_system == 'sysV':
            if not os.path.exists('distro/%s' %self.lnx_distro):
                msg = 'Unknown distribution "%s"' %self.lnx_distro
                msg += ', no entry in distro directory'
                sys.exit(1)

    def run(self):
        """
        Install the files for the Windows Azure Linux Agent
        """
        distro = self.lnx_distro
        init = self.init_system
        prefix = self.prefix
        tgtDir = self.root
        if prefix and prefix[-1] != '/':
            prefix += '/'
        else:
            prefix = '/'
        if tgtDir and tgtDir[-1] != '/':
            tgtDir += '/'
        else:
            tgtDir = '/'
        # Handle the different init systems
        if init == 'sysV':
            initdir = 'etc/init.d'
            if self.lnx_distro == 'redhat':
                initdir = 'etc/rc.d/init.d'
            if not os.path.exists(tgtDir + initdir):
                try:
                    self.mkpath(tgtDir + initdir, 0755)
                except:
                    msg = 'Could not create init script directory '
                    msg += tgtDir
                    msg += initdir
                    print msg
                    print sys.exc_info()[0]
                    sys.exit(1)
            initScripts = glob.glob('distro/%s/*.sysV' %distro)
            try:
                for f in initScripts:
                    newName = f.split('/')[-1].split('.')[0]
                    self.copy_file(f, tgtDir + initdir + '/' + newName)
            except:
                print 'Could not install systemV init script', 
                sys.exit(1)
        elif init == 'systemd':
            if not os.path.exists(tgtDir + prefix +'lib/systemd/system'):
                try:
                    self.mkpath(tgtDir + prefix + 'lib/systemd/system', 0755)
                except:
                    msg = 'Could not create systemd service directory '
                    msg += tgtDir + prefix
                    msg += 'lib/systemd/system'
                    print msg
                    sys.exit(1)
            services = glob.glob('distro/systemd/*')
            for f in services:
                try:
                    baseName = f.split('/')[-1]
                    self.copy_file(f,
                            tgtDir + prefix +'lib/systemd/system/' + baseName)
                except:
                    print 'Could not install systemd service files'
                    sys.exit(1)
        elif init == 'upstart':
            print 'Upstart init files installation not supported at this time.'
            print 'Need an implementation, please submit a patch ;)'
            print 'See WALinuxAgent/debian directory for Debian/Ubuntu packaging'
    
        # Configuration file
        if not os.path.exists(tgtDir + 'etc'):
                try:
                    self.mkpath(tgtDir + 'etc', 0755)
                except:
                    msg = 'Could not create config dir '
                    msg += tgtDir
                    msg += 'etc'
                    print msg
                    sys.exit(1)
        try:
            self.copy_file('config/waagent.conf', tgtDir + 'etc/waagent.conf')
        except:
            print 'Could not install configuration file %etc' %tgtDir
            sys.exit(1)
        if not os.path.exists(tgtDir + 'etc/logrotate.d'):
            try:
                self.mkpath(tgtDir + 'etc/logrotate.d', 0755)
            except:
                msg = 'Could not create ' + tgtDir + 'etc/logrotate.d'
                print msg
                sys.exit(1)
        try:
            self.copy_file('config/waagent.logrotate',
                      tgtDir + 'etc/logrotate.d/waagent')
        except:
            msg = 'Could not install logrotate file in '
            msg += tgtDir + 'etc/logrotate.d'
            print  msg
            sys.exit(1)
    
        # Daemon
        if not os.path.exists(tgtDir + prefix + 'sbin'):
            try:
                self.mkpath(tgtDir + prefix + 'sbin', 0755)
            except:
                msg = 'Could not create target daemon dir '
                msg+= tgtDir + prefix + 'sbin'
                print msg
                sys.exit(1)
        try:
            self.copy_file('waagent', tgtDir + prefix + 'sbin/waagent')
        except:
            print 'Could not install daemon %s%ssbin/waagent' %(tgtDir,prefix)
            sys.exit(1)
        os.chmod('%s%ssbin/waagent' %(tgtDir,prefix), 0755)

def readme():
    with open('README') as f:
        return f.read()
    
setuptools.setup(name = 'waagent',
      version = '1.4.0',
      description = 'Windows Azure Linux Agent',
      long_description = readme(),
      author = 'Stephen Zarkos, Eric Gable',
      author_email = 'walinuxagent@microsoft.com',
      platforms = 'Linux',
      url = 'https://github.com/Windows-Azure/',
      license = 'Apache License Version 2.0',
      cmdclass = {
          # Use a subclass for install that handles
          # install, we do not have a "true" python package
          'install': InstallData,
      },
)



=======

import os
from azurelinuxagent.common.version import AGENT_NAME, AGENT_VERSION, \
    AGENT_DESCRIPTION, \
    DISTRO_NAME, DISTRO_VERSION, DISTRO_FULL_NAME

from azurelinuxagent.common.osutil import get_osutil
import setuptools
from setuptools import find_packages
from setuptools.command.install import install as  _install

root_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(root_dir)


def set_files(data_files, dest=None, src=None):
    data_files.append((dest, src))


def set_bin_files(data_files, dest="/usr/sbin",
                  src=["bin/waagent", "bin/waagent2.0"]):
    data_files.append((dest, src))


def set_conf_files(data_files, dest="/etc", src=["config/waagent.conf"]):
    data_files.append((dest, src))


def set_logrotate_files(data_files, dest="/etc/logrotate.d",
                        src=["config/waagent.logrotate"]):
    data_files.append((dest, src))


def set_sysv_files(data_files, dest="/etc/rc.d/init.d", src=["init/waagent"]):
    data_files.append((dest, src))


def set_systemd_files(data_files, dest="/lib/systemd/system",
                      src=["init/waagent.service"]):
    data_files.append((dest, src))


def set_rc_files(data_files, dest="/etc/rc.d/", src=["init/freebsd/waagent"]):
    data_files.append((dest, src))


def set_udev_files(data_files, dest="/etc/udev/rules.d/",
                   src=["config/66-azure-storage.rules",
                        "config/99-azure-product-uuid.rules"]):
    data_files.append((dest, src))


def get_data_files(name, version, fullname):
    """
    Determine data_files according to distro name, version and init system type
    """
    data_files = []

    if name == 'redhat' or name == 'centos':
        set_bin_files(data_files)
        set_conf_files(data_files)
        set_logrotate_files(data_files)
        set_udev_files(data_files)
        if version.startswith("6"):
            set_sysv_files(data_files)
        else:
            # redhat7.0+ use systemd
            set_systemd_files(data_files, dest="/usr/lib/systemd/system")
            if version.startswith("7.1"):
                # TODO this is a mitigation to systemctl bug on 7.1
                set_sysv_files(data_files)

    elif name == 'arch':
        set_bin_files(data_files, dest="/usr/bin")
        set_conf_files(data_files, src=["config/arch/waagent.conf"])
        set_udev_files(data_files)
        set_systemd_files(data_files, dest='/usr/lib/systemd/system',
                          src=["init/arch/waagent.service"])
    elif name == 'coreos':
        set_bin_files(data_files, dest="/usr/share/oem/bin")
        set_conf_files(data_files, dest="/usr/share/oem",
                       src=["config/coreos/waagent.conf"])
        set_logrotate_files(data_files)
        set_udev_files(data_files)
        set_files(data_files, dest="/usr/share/oem",
                  src=["init/coreos/cloud-config.yml"])
    elif name == 'clear linux software for intel architecture':
        set_bin_files(data_files, dest="/usr/bin")
        set_conf_files(data_files, dest="/usr/share/defaults/waagent",
                       src=["config/clearlinux/waagent.conf"])
        set_systemd_files(data_files, dest='/usr/lib/systemd/system',
                          src=["init/clearlinux/waagent.service"])
    elif name == 'ubuntu':
        set_bin_files(data_files)
        set_conf_files(data_files, src=["config/ubuntu/waagent.conf"])
        set_logrotate_files(data_files)
        set_udev_files(data_files, src=["config/99-azure-product-uuid.rules"])
        if version.startswith("12") or version.startswith("14"):
            # Ubuntu12.04/14.04 - uses upstart
            set_files(data_files, dest="/etc/init",
                      src=["init/ubuntu/walinuxagent.conf"])
            set_files(data_files, dest='/etc/default',
                      src=['init/ubuntu/walinuxagent'])
        elif fullname == 'Snappy Ubuntu Core':
            set_files(data_files, dest="<TODO>",
                      src=["init/ubuntu/snappy/walinuxagent.yml"])
        else:
            # Ubuntu15.04+ uses systemd
            set_systemd_files(data_files,
                              src=["init/ubuntu/walinuxagent.service"])
    elif name == 'suse':
        set_bin_files(data_files)
        set_conf_files(data_files, src=["config/suse/waagent.conf"])
        set_logrotate_files(data_files)
        set_udev_files(data_files)
        if fullname == 'SUSE Linux Enterprise Server' and \
                version.startswith('11') or \
                                fullname == 'openSUSE' and version.startswith(
                    '13.1'):
            set_sysv_files(data_files, dest='/etc/init.d',
                           src=["init/suse/waagent"])
        else:
            # sles 12+ and openSUSE 13.2+ use systemd
            set_systemd_files(data_files, dest='/usr/lib/systemd/system')
    elif name == 'freebsd':
        set_bin_files(data_files, dest="/usr/local/sbin")
        set_conf_files(data_files, src=["config/freebsd/waagent.conf"])
        set_rc_files(data_files)
    else:
        # Use default setting
        set_bin_files(data_files)
        set_conf_files(data_files)
        set_logrotate_files(data_files)
        set_udev_files(data_files)
        set_sysv_files(data_files)
    return data_files


class install(_install):
    user_options = _install.user_options + [
        ('lnx-distro=', None, 'target Linux distribution'),
        ('lnx-distro-version=', None, 'target Linux distribution version'),
        ('lnx-distro-fullname=', None, 'target Linux distribution full name'),
        ('register-service', None, 'register as startup service and start'),
        ('skip-data-files', None, 'skip data files installation'),
    ]

    def initialize_options(self):
        _install.initialize_options(self)
        self.lnx_distro = DISTRO_NAME
        self.lnx_distro_version = DISTRO_VERSION
        self.lnx_distro_fullname = DISTRO_FULL_NAME
        self.register_service = False
        self.skip_data_files = False

    def finalize_options(self):
        _install.finalize_options(self)
        if self.skip_data_files:
            return

        data_files = get_data_files(self.lnx_distro, self.lnx_distro_version,
                                    self.lnx_distro_fullname)
        self.distribution.data_files = data_files
        self.distribution.reinitialize_command('install_data', True)

    def run(self):
        _install.run(self)
        if self.register_service:
            osutil = get_osutil()
            osutil.register_agent_service()
            osutil.stop_agent_service()
            osutil.start_agent_service()


setuptools.setup(
    name=AGENT_NAME,
    version=AGENT_VERSION,
    long_description=AGENT_DESCRIPTION,
    author='Microsoft Corporation',
    author_email='walinuxagent@microsoft.com',
    platforms='Linux',
    url='https://github.com/Azure/WALinuxAgent',
    license='Apache License Version 2.0',
    packages=find_packages(exclude=["tests"]),
    py_modules=["__main__"],
    cmdclass={
        'install': install
    }
)
>>>>>>> 6883b02ac1cfe31db7d9797dde4504fb471f9954
