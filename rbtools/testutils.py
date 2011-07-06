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

    def in_path(self, binary):
        """Checks whether an executable is in the user's search path.

        This expects a name without any system-specific executable extension.
        It will append the proper extension as necessary. For example,
        use "myapp" and not "myapp.exe".

        This will return True if the app is in the path, or False otherwise.

        Taken from djblets.util.filesystem to avoid an extra dependency
            """
        if sys.platform == 'win32' and not binary.endswith('.exe'):
            binary += ".exe"

        for dir in os.environ['PATH'].split(os.pathsep):
            if os.path.exists(os.path.join(dir, binary)):
                return True

        return False

    def reset_cl_args(self, values=[]):
        sys.argv = values

    def set_user_home(self, path):
        os.environ['HOME'] = path

    def set_user_home_tmp(self):
        self.set_user_home(mkdtemp())
