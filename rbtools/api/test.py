import os
import sys
import unittest

from tempfile import mkdtemp

from rbtools.api.settings import Settings, CONFIG_NAME
from rbtools.api.utilities import  RBUtilities

TEST_SERVER = 'localhost'
TEST_USER = 'tester'

class SettingsTest(unittest.TestCase):

    def set_fake_settings(self, settings):
        settings.reviewboard_url =  TEST_SERVER
        settings.user = TEST_USER

    def check_fake_settings(self, settings):
        self.assertTrue(settings.reviewboard_url == TEST_SERVER)
        self.assertTrue(settings.user == TEST_USER)

    def test_get_settings(self):
        os.chdir(mkdtemp())
        f = open(CONFIG_NAME, 'w')
        f.write(FAKE_CONFIG)
        f.close()

        settings = Settings()
        settings.load()
        self.check_fake_settings(settings)

    def test_set_settings(self):
        settings = Settings()
        self.set_fake_settings(settings)
        self.check_fake_settings(settings)

    def test_save_and_load_settings(self):
        os.chdir(mkdtemp())
        settings = Settings()
        self.set_fake_settings(settings)
        settings.save(CONFIG_NAME)

        settings = Settings()
        settings.load()
        self.check_fake_settings(settings)

    def test_attrs(self):
        """Settings class is know to overwrite __getattr__ and __setattr__"""
        """this test checks that we still can get/set regular attributes"""
        settings = Settings()
        test_value = [[dict()]]
        settings.some_non_config_value = test_value
        self.assertEquals(settings.some_non_config_value, test_value)


class UtilitiesTest(unittest.TestCase):

    def test_check_install(self):
        util = RBUtilities()
        self.assertTrue(util.check_install(sys.executable + ' --version'))
        self.assertFalse(util.check_install('3F2504E0-4F89-11D3-9A0C-0305E82C3301'))

    def test_make_tempfile(self):
        util = RBUtilities()
        fname = util.make_tempfile()

        self.assertTrue(os.path.isfile(fname))
        self.assertEqual(os.stat(fname).st_uid, os.geteuid())
        self.assertTrue(os.access(fname, os.R_OK | os.W_OK))

    def test_execute(self):
        util = RBUtilities()

        self.assertRegexpMatches(util.execute([sys.executable, '--version']),
                                 '^[Pp][Yy][Tt][Hh][Oo][Nn]\s+(\d+\.?)+$')

    def test_die(self):
        util = RBUtilities()

        with self.assertRaises(SystemExit) as rc:
            util.die()
        self.assertEqual(rc.exception.code, 1)


FAKE_CONFIG = """\
[main]

ReVIeWBoard_UrL = %s

USer = %s
""" % (TEST_SERVER, TEST_USER)
