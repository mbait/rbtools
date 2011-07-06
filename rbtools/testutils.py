import os
import sys
import unittest
import uuid

from tempfile import mkdtemp


class RBTestBase(unittest.TestCase):

    def setUp(self):
        self.set_user_home_tmp()

    def chdir_tmp(self, dir=None):
        dname = mkdtemp(dir=dir)
        os.chdir(dname)
        return dname

    def gen_uuid(self):
        return str(uuid.uuid4())

    def get_user_home(self):
        return os.environ['HOME']

    def reset_cl_args(self, values=[]):
        sys.argv = values

    def set_user_home(self, path):
        os.environ['HOME'] = path

    def set_user_home_tmp(self):
        self.set_user_home(mkdtemp())
