import os
import unittest
import uuid

from tempfile import mkdtemp


SETTINGS_ATTRS = [
    'reviewboard_url',
    'user',
    'cookie_file'
]


class RBTestBase(unittest.TestCase):

    def chdir_tmp(self, dir=None):
        return os.chdir(mkdtemp(dir=dir))

    def gen_uuid(self):
        return str(uuid.uuid4())

    def get_user_home(self):
        return os.environ['HOME']

    def set_user_home(self, path):
        os.environ['HOME'] = path

    def set_user_home_tmp(self):
        self.set_user_home(mkdtemp())


class SettingsTestBase(RBTestBase):

    def check_fake_settings(self, settings, samples):
        for name in samples:
            self.assertEqual(getattr(settings, name), samples[name])

    def set_fake_settings(self, settings, attrs=SETTINGS_ATTRS):
        fake_data = {}
        for name in attrs:
            fake_data[name] = self.gen_uuid()
            setattr(settings, name, fake_data[name])

        return fake_data
