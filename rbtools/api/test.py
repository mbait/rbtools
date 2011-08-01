"""Tests for rbtools.api units.

Any new modules created under rbtools/api should be tested here."""
import os
import sys

from rbtools.api.settings import Settings
from rbtools.api.utilities import  RBUtilities
from rbtools.util.testutil import RBTestBase


SETTINGS_ATTRS = [
    'reviewboard_url',
    'user',
    'cookie_file'
]


class SettingsTest(RBTestBase):
    """Check saving/loading of user settings."""
    def check_fake_settings(self, settings, samples):
        """Validate test settings."""
        for name in samples:
            self.assertEqual(getattr(settings, name), samples[name])

    def set_fake_settings(self, settings, attrs=SETTINGS_ATTRS):
        """Set some fake values which will be checked after test run."""
        fake_data = {}
        for name in attrs:
            fake_data[name] = self.gen_uuid()
            setattr(settings, name, fake_data[name])

        return fake_data

    def test_set_settings(self):
        """Merely check possibility to set settings fields."""
        settings = Settings()
        data = self.set_fake_settings(settings)
        self.check_fake_settings(settings, data)

    def test_save_and_load_settings(self):
        """Test saving then loading settings from a file."""
        self.chdir_tmp()
        settings = Settings()
        data = self.set_fake_settings(settings)
        settings.save_local()

        settings = Settings()
        settings.load()
        self.check_fake_settings(settings, data)

    def test_set_attr(self):
        """Settings class is know to overwrite __getattr__ and __setattr__,
        this test checks that we still can get/set regular attributes."""
        settings = Settings()
        test_value = [[dict()]]
        settings.some_non_config_value = test_value
        self.assertEquals(settings.some_non_config_value, test_value)

    def test_get_attr(self):
        """Test if access to unexisting attribute raises AttributeError."""
        settings = Settings()
        with self.assertRaises(AttributeError):
            settings.another_fake_attribute

    def test_use_global(self):
        """Test settings operations at global level."""
        self.chdir_tmp(dir=self.get_user_home())
        settings = Settings()
        data = self.set_fake_settings(settings)
        settings.save_global()

        settings = Settings()
        settings.load()
        self.check_fake_settings(settings, data)

    def test_use_local_and_global(self):
        """Test settings operations at different levels."""
        self.set_user_home_tmp()
        self.chdir_tmp(dir=self.get_user_home())
        settings = Settings()
        global_data = self.set_fake_settings(settings, attrs=['cookie_file'])
        settings.save_global()

        settings = Settings()
        local_data = self.set_fake_settings(settings, attrs=['user'])
        settings.save_local()

        settings = Settings()
        settings.load()
        global_data.update(local_data)
        self.check_fake_settings(settings, global_data)


class UtilitiesTest(RBTestBase):

    def test_check_install(self):
        """Test 'check_install' method."""
        util = RBUtilities()
        self.assertTrue(util.check_install(sys.executable + ' --version'))
        self.assertFalse(util.check_install(self.gen_uuid()))

    def test_make_tempfile(self):
        """Test 'make_tempfile' method."""
        util = RBUtilities()
        fname = util.make_tempfile()

        self.assertTrue(os.path.isfile(fname))
        self.assertEqual(os.stat(fname).st_uid, os.geteuid())
        self.assertTrue(os.access(fname, os.R_OK | os.W_OK))

    def test_execute(self):
        """Test 'execute' method."""
        util = RBUtilities()

        self.assertRegexpMatches(util.execute([sys.executable, '--version']),
                                 '%d.%d.%d' % sys.version_info[:3])

    def test_die(self):
        """Test 'die' method."""
        util = RBUtilities()

        with self.assertRaises(SystemExit) as rc:
            util.die()
        self.assertEqual(rc.exception.code, 1)
