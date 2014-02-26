import unittest
import hod.commands.command as hcc

class HodCommandsCommandTestCase(unittest.TestCase):
    @unittest.expectedFailure
    def test_command_breathing(self):
        c = hcc.Command()
        assert str(c) == ''

    def test_command_empty_run(self):
        c = hcc.Command()
        assert c.run() is None

    def test_command_run_true(self):
        c = hcc.Command('true')
        out, err = c.run()
        assert out == ''
        assert err == ''

    def test_command_true_fake_pty(self):
        c = hcc.Command('true')
        c.fake_ptr = True
        out, err = c.run()
        assert out == ''
        assert err == ''

    def test_command_sleep(self):
        c = hcc.Command(['sleep', '1']) # sadly this takes time... :(
        out, err = c.run()
        assert out == ''
        assert err == ''

    def test_command_run_echo_hello(self):
        c = hcc.Command('echo hello')
        out, err = c.run()
        assert out == 'hello'
        assert err == ''

    def test_command_run_echo_hello_stderr(self):
        c = hcc.Command('echo hello 1>&2')
        out, err = c.run()
        assert out == ''
        assert err == 'hello'

    def test_ipaddrshow(self):
        c = hcc.IpAddrShow()
        assert str(c) == '/sbin/ip addr show'
        out, err = c.run()
        print 'out', out
        print 'err', err
        assert out != '' # loads of text which is different on each platform
        assert err == '' # Probably won't work on non Linux.

    def test_java_command(self):
        c = hcc.JavaCommand('-version')
        assert str(c) == 'java -version'
        out, err = c.run()
        assert out == ''
        assert err.startswith('java version "1')

    def test_java_version(self):
        c = hcc.JavaVersion()
        assert str(c) == 'java -version'
        out, err = c.run()
        assert out.startswith('\njava version "1')
        assert err.startswith('java version "1')

    def test_generate_ssh_key(self):
        c = hcc.GenerateSshKey('.')
        assert str(c) == '/usr/bin/ssh-keygen -t rsa -b 2048 -N "" -f .' 

    def test_run_ssdh(self):
        c = hcc.RunSshd('.')
        assert str(c) == '/usr/sbin/sshd -f .'

    def test_kill_pid_file(self):
        c = hcc.KillPidFile('wibble')
        assert str(c) == 'None' # wat.
        self.assertRaises(IOError, c.run)

    def test_screen_daemon(self):
        name = 'hanythingondemand-unittest-screen-daemon'
        c = hcc.ScreenDaemon(name)
        assert str(c) == 'screen -dmS dummyxc screen -S %s' % name

    def test_run_in_screen(self):
        name = 'hanythingondemand-unittest-run-in-screen'
        c = hcc.RunInScreen(name)
        assert str(c) == name
