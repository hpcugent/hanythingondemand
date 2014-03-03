###
# Copyright 2009-2014 Ghent University
#
# This file is part of hanythingondemand
# originally created by the HPC team of Ghent University (http://ugent.be/hpc/en),
# with support of Ghent University (http://ugent.be/hpc),
# the Flemish Supercomputer Centre (VSC) (https://vscentrum.be/nl/en),
# the Hercules foundation (http://www.herculesstichting.be/in_English)
# and the Department of Economy, Science and Innovation (EWI) (http://www.ewi-vlaanderen.be/en).
#
# http://github.com/hpcugent/hanythingondemand
#
# hanythingondemand is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation v2.
#
# hanythingondemand is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with hanythingondemand. If not, see <http://www.gnu.org/licenses/>.
import unittest
import hod.commands.command as hcc

class HodCommandsCommandTestCase(unittest.TestCase):
    @unittest.expectedFailure
    def test_command_breathing(self):
        c = hcc.Command()
        self.assertEqual(str(c), '')

    def test_command_empty_run(self):
        c = hcc.Command()
        self.assertTrue(c.run() is None)

    def test_command_run_true(self):
        c = hcc.Command('true')
        out, err = c.run()
        self.assertEqual(out, '')
        self.assertEqual(err, '')

    def test_command_true_fake_pty(self):
        c = hcc.Command('true')
        c.fake_ptr = True
        out, err = c.run()
        self.assertEqual(out, '')
        self.assertEqual(err, '')

    def test_command_sleep(self):
        c = hcc.Command(['sleep', '1']) # sadly this takes time... :(
        out, err = c.run()
        self.assertEqual(out, '')
        self.assertEqual(err, '')

    def test_command_run_echo_hello(self):
        c = hcc.Command('echo hello')
        out, err = c.run()
        self.assertEqual(out, 'hello')
        self.assertEqual(err, '')

    def test_command_run_echo_hello_stderr(self):
        c = hcc.Command('echo hello 1>&2')
        out, err = c.run()
        self.assertEqual(out, '')
        self.assertEqual(err, 'hello')

    def test_ipaddrshow(self):
        c = hcc.IpAddrShow()
        self.assertEqual(str(c), '/sbin/ip addr show')
        out, err = c.run()
        print 'out', out
        print 'err', err
        self.assertNotEqual(out,  '') # loads of text which is different on each platform
        self.assertEqual(err, '') # Probably won't work on non Linux.

    def test_java_command(self):
        c = hcc.JavaCommand('-version')
        self.assertEqual(str(c), 'java -version')
        out, err = c.run()
        self.assertEqual(out, '')
        self.assertTrue(err.startswith('java version "1'))

    def test_java_version(self):
        c = hcc.JavaVersion()
        self.assertEqual(str(c), 'java -version')
        out, err = c.run()
        self.assertTrue(out.startswith('\njava version "1'))
        self.assertTrue(err.startswith('java version "1'))

    def test_generate_ssh_key(self):
        c = hcc.GenerateSshKey('.')
        self.assertEqual(str(c), '/usr/bin/ssh-keygen -t rsa -b 2048 -N "" -f .' )

    def test_run_ssdh(self):
        c = hcc.RunSshd('.')
        self.assertEqual(str(c), '/usr/sbin/sshd -f .')

    def test_kill_pid_file(self):
        c = hcc.KillPidFile('wibble')
        self.assertEqual(str(c), 'None') # wat.
        self.assertRaises(IOError, c.run)

    def test_screen_daemon(self):
        name = 'hanythingondemand-unittest-screen-daemon'
        c = hcc.ScreenDaemon(name)
        self.assertEqual(str(c), 'screen -dmS dummyxc screen -S %s' % name)

    def test_run_in_screen(self):
        name = 'hanythingondemand-unittest-run-in-screen'
        c = hcc.RunInScreen(name)
        self.assertEqual(str(c), name)
