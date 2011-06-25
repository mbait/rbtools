import os
import sys
import unittest

from tempfile import mkdtemp

from rbtools.api.settings import Settings
from rbtools.commands.rbconfig import main as rbconfig_main
from rbtools.testutils import TEST_COOKIE_FILE, TEST_SERVER, TEST_USER


class RBConfigTest(unittest.TestCase):

    def _set_and_check_options(self, opts):
        sys.argv = opts
        os.chdir(mkdtemp())
        rbconfig_main()

        settings = Settings()
        settings.load()
        self.assertEqual(settings.reviewboard_url, TEST_SERVER)
        self.assertEqual(settings.user, TEST_USER)
        self.assertEqual(settings.cookie_file, TEST_COOKIE_FILE)

    def test_run_blank(self):
        # Without any argument program should still exit with zero error code.
        sys.argv = []
        try:
            rbconfig_main()
        except Exception:
            self.fail()

    def test_set_options(self):
        self._set_and_check_options(['', '-u', TEST_USER, '-U', TEST_SERVER,
                                     '-c', TEST_COOKIE_FILE])

    def test_set_options_long(self):
        self._set_and_check_options(['', '--user', TEST_USER, '--url', TEST_SERVER,
                                     '--cookie-file', TEST_COOKIE_FILE])
