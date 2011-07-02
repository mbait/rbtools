import os
import sys

from rbtools.api.settings import Settings
from rbtools.api.utilities import  RBUtilities
from rbtools.testutils import RBTestBase, SettingsTestBase


class SettingsTest(SettingsTestBase):

    def setUp(self):
        self.set_user_home_tmp()

    def test_set_settings(self):
        settings = Settings()
        data = self.set_fake_settings(settings)
        self.check_fake_settings(settings, data)

    def test_save_and_load_settings(self):
        self.chdir_tmp()
        settings = Settings()
        data = self.set_fake_settings(settings)
        settings.save_local()

        settings = Settings()
        settings.load()
        self.check_fake_settings(settings, data)

    def test_set_attr(self):
        """Settings class is know to overwrite __getattr__ and __setattr__"""
        """this test checks that we still can get/set regular attributes"""
        settings = Settings()
        test_value = [[dict()]]
        settings.some_non_config_value = test_value
        self.assertEquals(settings.some_non_config_value, test_value)

    def test_get_attr(self):
        settings = Settings()
        with self.assertRaises(AttributeError):
            settings.another_fake_attribute

    def test_use_global(self):
        self.chdir_tmp(dir=self.get_user_home())
        settings = Settings()
        data = self.set_fake_settings(settings)
        settings.save_global()

        settings = Settings()
        settings.load()
        self.check_fake_settings(settings, data)

    def test_use_local_and_global(self):
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
        util = RBUtilities()
        self.assertTrue(util.check_install(sys.executable + ' --version'))
        self.assertFalse(util.check_install(self.gen_uuid()))

    def test_make_tempfile(self):
        util = RBUtilities()
        fname = util.make_tempfile()

        self.assertTrue(os.path.isfile(fname))
        self.assertEqual(os.stat(fname).st_uid, os.geteuid())
        self.assertTrue(os.access(fname, os.R_OK | os.W_OK))

    def test_execute(self):
        util = RBUtilities()

        self.assertRegexpMatches(util.execute([sys.executable, '--version']),
                                 '%d.%d.%d' % sys.version_info[:3])

    def test_die(self):
        util = RBUtilities()

        with self.assertRaises(SystemExit) as rc:
            util.die()
        self.assertEqual(rc.exception.code, 1)
