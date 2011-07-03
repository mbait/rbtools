import sys

from rbtools.api.settings import Settings
from rbtools.commands.rbconfig import main as rbconfig
from rbtools.testutils import RBTestBase


OPT_MAPPINGS = {
    '-U': 'reviewboard_url',
    '-u': 'user',
    '-c': 'cookie_file',
    '--url': 'reviewboard_url',
    '--user': 'user',
    '--cookie-file': 'cookie_file'
}


class RBConfigTest(RBTestBase):

    def setUp(self):
        self.set_user_home_tmp()

    def check_loaded_values(self, settings, samples):
        for name in samples:
            self.assertEqual(samples[name], getattr(settings, name))

    def set_fake_values(self, *opts):
        args = ['']
        data = {}
        for name, value in [(name, self.gen_uuid()) for name in opts]:
            args.append(name)
            args.append(value)
            data[OPT_MAPPINGS[name]] = value

        self.reset_cl_args(values=args)
        return data

    def test_run_blank(self):
        # Without any arguments program should still exit with zero error code.
        self.reset_cl_args()
        try:
            rbconfig()
        except Exception:
            self.fail()

    def test_set_options_short(self):
        self.chdir_tmp()
        data = self.set_fake_values('-u', '-U', '-c')
        rbconfig()

        settings = Settings()
        settings.load()
        self.check_loaded_values(settings, data)

    def test_set_options_long(self):
        self.chdir_tmp()
        data = self.set_fake_values('--user', '--url', '--cookie-file')
        rbconfig()

        settings = Settings()
        settings.load()
        self.check_loaded_values(settings, data)

    def test_set_options_mixed(self):
        self.chdir_tmp()
        data = self.set_fake_values('-c', '--user')
        rbconfig()

        settings = Settings()
        settings.load()
        self.check_loaded_values(settings, data)

    def test_set_options_global(self):
        self.chdir_tmp()
        data = self.set_fake_values('-u', '-U', '-c')
        sys.argv.append('--global')
        rbconfig()

        settings = Settings()
        settings.load()
        self.check_loaded_values(settings, data)

    def test_set_options_local_and_global(self):
        self.chdir_tmp()
        data = self.set_fake_values('-u', '-U')
        sys.argv.append('--global')
        rbconfig()

        self.chdir_tmp(dir=self.get_user_home())
        data.update(self.set_fake_values('--cookie-file'))
        rbconfig()

        settings = Settings()
        settings.load()
        self.check_loaded_values(settings, data)
