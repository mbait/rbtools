import nose

from rbtools.clients.client import Repository
from rbtools.clients.git import GitClient
from rbtools.testutils import RBTestBase

TEST_FILE = 'foo.txt'


class GitClientTest(RBTestBase):

    def setUp(self):
        self.git = GitClient()
        if not self.in_path('git'):
            raise nose.SkipTest('git not found in path')

        self.set_user_home_tmp()

    def clone(self):
        initial = self.chdir_tmp()
        self.git.run_command(['init'])
        self.add_file(TEST_FILE, FOO)
        cloned = self.chdir_tmp()
        self.git.run_command(['clone', initial, cloned])

    def add_file(self, name,content):
        foo = open(name, 'w')
        foo.write(content)
        foo.close()
        self.git.run_command(['add', name])
        self.git.run_command(['commit', '-m', "''",
                             '--author=A U Thor <author@example.com>'])

    def test_installed(self):
        self.assertTrue(self.git.installed)

    def test_get_repository_info_simple(self):
        """Test GitClient get_repository_info, simple case"""
        self.clone()
        repo = self.git.get_info()
        self.assertTrue(isinstance(repo, Repository))
        self.assertEqual(repo.base_path, '')
        self.assertTrue(repo.supports_parent_diffs)
        self.assertFalse(repo.supports_changesets)

    def test_scan_for_server_simple(self):
        """Test GitClient scan_for_server, simple case"""
        pass
        """
        self.chdir_tmp()
        self.clone()
        repo = self.git.get_info()
        server = self.git.scan_for_server(repo)
        self.assertIsNone(server)
        """

    def test_scan_for_server_reviewboardrc(self):
        "Test GitClient scan_for_server, .reviewboardrc case"""
        pass
        """
        os.chdir(self.clone_dir)
        rc = open(os.path.join(self.clone_dir, '.reviewboardrc'), 'w')
        rc.write('REVIEWBOARD_URL = "%s"' % self.TESTSERVER)
        rc.close()

        ri = self.client.get_repository_info()
        server = self.client.scan_for_server(ri)
        self.assertEqual(server, self.TESTSERVER)
        """

    def test_scan_for_server_property(self):
        """Test GitClient scan_for_server using repo property"""
        pass
        """
        os.chdir(self.clone_dir)
        self._gitcmd(['config', 'reviewboard.url', self.TESTSERVER])
        ri = self.client.get_repository_info()

        self.assertEqual(self.client.scan_for_server(ri), self.TESTSERVER)
        """

    def test_diff_simple(self):
        """Test GitClient simple diff case"""
        diff = "diff --git a/foo.txt b/foo.txt\n" \
               "index 634b3e8ff85bada6f928841a9f2c505560840b3a..5e98e9540e1b741b5be24fcb33c40c1c8069c1fb 100644\n" \
               "--- a/foo.txt\n" \
               "+++ b/foo.txt\n" \
               "@@ -6,7 +6,4 @@ multa quoque et bello passus, dum conderet urbem,\n" \
               " inferretque deos Latio, genus unde Latinum,\n" \
               " Albanique patres, atque altae moenia Romae.\n" \
               " Musa, mihi causas memora, quo numine laeso,\n" \
               "-quidve dolens, regina deum tot volvere casus\n" \
               "-insignem pietate virum, tot adire labores\n" \
               "-impulerit. Tantaene animis caelestibus irae?\n" \
               " \n"

        self.clone()
        self.git.get_info()
        self.add_file('foo.txt', FOO1)
        self.assertEqual(self.git.diff(None), (diff, None))

    def test_diff_simple_multiple(self):
        """Test GitClient simple diff with multiple commits case"""
        diff = "diff --git a/foo.txt b/foo.txt\n" \
               "index 634b3e8ff85bada6f928841a9f2c505560840b3a..63036ed3fcafe870d567a14dd5884f4fed70126c 100644\n" \
               "--- a/foo.txt\n" \
               "+++ b/foo.txt\n" \
               "@@ -1,12 +1,11 @@\n" \
               " ARMA virumque cano, Troiae qui primus ab oris\n" \
               "+ARMA virumque cano, Troiae qui primus ab oris\n" \
               " Italiam, fato profugus, Laviniaque venit\n" \
               " litora, multum ille et terris iactatus et alto\n" \
               " vi superum saevae memorem Iunonis ob iram;\n" \
               "-multa quoque et bello passus, dum conderet urbem,\n" \
               "+dum conderet urbem,\n" \
               " inferretque deos Latio, genus unde Latinum,\n" \
               " Albanique patres, atque altae moenia Romae.\n" \
               "+Albanique patres, atque altae moenia Romae.\n" \
               " Musa, mihi causas memora, quo numine laeso,\n" \
               "-quidve dolens, regina deum tot volvere casus\n" \
               "-insignem pietate virum, tot adire labores\n" \
               "-impulerit. Tantaene animis caelestibus irae?\n" \
               " \n"

        self.clone()
        self.git.get_info()
        self.add_file(TEST_FILE, FOO1)
        self.add_file(TEST_FILE, FOO2)
        self.add_file(TEST_FILE, FOO3)

        self.assertEqual(self.git.diff(None), (diff, None))

    def test_diff_branch_diverge(self):
        """Test GitClient diff with divergent branches"""
        pass
        """
        diff1 = "diff --git a/foo.txt b/foo.txt\n" \
                "index 634b3e8ff85bada6f928841a9f2c505560840b3a..e619c1387f5feb91f0ca83194650bfe4f6c2e347 100644\n" \
                "--- a/foo.txt\n" \
                "+++ b/foo.txt\n" \
                "@@ -1,4 +1,6 @@\n" \
                " ARMA virumque cano, Troiae qui primus ab oris\n" \
                "+ARMA virumque cano, Troiae qui primus ab oris\n" \
                "+ARMA virumque cano, Troiae qui primus ab oris\n" \
                " Italiam, fato profugus, Laviniaque venit\n" \
                " litora, multum ille et terris iactatus et alto\n" \
                " vi superum saevae memorem Iunonis ob iram;\n" \
                "@@ -6,7 +8,4 @@ multa quoque et bello passus, dum conderet urbem,\n" \
                " inferretque deos Latio, genus unde Latinum,\n" \
                " Albanique patres, atque altae moenia Romae.\n" \
                " Musa, mihi causas memora, quo numine laeso,\n" \
                "-quidve dolens, regina deum tot volvere casus\n" \
                "-insignem pietate virum, tot adire labores\n" \
                "-impulerit. Tantaene animis caelestibus irae?\n" \
                " \n"

        diff2 = "diff --git a/foo.txt b/foo.txt\n" \
                "index 634b3e8ff85bada6f928841a9f2c505560840b3a..5e98e9540e1b741b5be24fcb33c40c1c8069c1fb 100644\n" \
                "--- a/foo.txt\n" \
                "+++ b/foo.txt\n" \
                "@@ -6,7 +6,4 @@ multa quoque et bello passus, dum conderet urbem,\n" \
                " inferretque deos Latio, genus unde Latinum,\n" \
                " Albanique patres, atque altae moenia Romae.\n" \
                " Musa, mihi causas memora, quo numine laeso,\n" \
                "-quidve dolens, regina deum tot volvere casus\n" \
                "-insignem pietate virum, tot adire labores\n" \
                "-impulerit. Tantaene animis caelestibus irae?\n" \
                " \n"

        os.chdir(self.clone_dir)

        self._git_add_file_commit('foo.txt', FOO1, 'commit 1')

        self._gitcmd(['checkout', '-b', 'mybranch', '--track', 'origin/master'])
        self._git_add_file_commit('foo.txt', FOO2, 'commit 2')

        self.client.get_repository_info()
        self.assertEqual(self.client.diff(None), (diff1, None))

        self._gitcmd(['checkout', 'master'])
        self.client.get_repository_info()
        self.assertEqual(self.client.diff(None), (diff2, None))
        """

    def test_diff_tracking_no_origin(self):
        """Test GitClient diff with a tracking branch, but no origin remote"""
        pass
        """
        diff = "diff --git a/foo.txt b/foo.txt\n" \
               "index 634b3e8ff85bada6f928841a9f2c505560840b3a..5e98e9540e1b741b5be24fcb33c40c1c8069c1fb 100644\n" \
               "--- a/foo.txt\n" \
               "+++ b/foo.txt\n" \
               "@@ -6,7 +6,4 @@ multa quoque et bello passus, dum conderet urbem,\n" \
               " inferretque deos Latio, genus unde Latinum,\n" \
               " Albanique patres, atque altae moenia Romae.\n" \
               " Musa, mihi causas memora, quo numine laeso,\n" \
               "-quidve dolens, regina deum tot volvere casus\n" \
               "-insignem pietate virum, tot adire labores\n" \
               "-impulerit. Tantaene animis caelestibus irae?\n" \
               " \n"

        os.chdir(self.clone_dir)

        self._gitcmd(['remote', 'add', 'quux', self.git_dir])
        self._gitcmd(['fetch', 'quux'])
        self._gitcmd(['checkout', '-b', 'mybranch', '--track', 'quux/master'])
        self._git_add_file_commit('foo.txt', FOO1, 'delete and modify stuff')

        self.client.get_repository_info()

        self.assertEqual(self.client.diff(None), (diff, None))
        """

    def test_diff_local_tracking(self):
        """Test GitClient diff with a local tracking branch"""
        pass
        """
        diff = "diff --git a/foo.txt b/foo.txt\n" \
               "index 634b3e8ff85bada6f928841a9f2c505560840b3a..e619c1387f5feb91f0ca83194650bfe4f6c2e347 100644\n" \
               "--- a/foo.txt\n" \
               "+++ b/foo.txt\n" \
               "@@ -1,4 +1,6 @@\n" \
               " ARMA virumque cano, Troiae qui primus ab oris\n" \
               "+ARMA virumque cano, Troiae qui primus ab oris\n" \
               "+ARMA virumque cano, Troiae qui primus ab oris\n" \
               " Italiam, fato profugus, Laviniaque venit\n" \
               " litora, multum ille et terris iactatus et alto\n" \
               " vi superum saevae memorem Iunonis ob iram;\n" \
               "@@ -6,7 +8,4 @@ multa quoque et bello passus, dum conderet urbem,\n" \
               " inferretque deos Latio, genus unde Latinum,\n" \
               " Albanique patres, atque altae moenia Romae.\n" \
               " Musa, mihi causas memora, quo numine laeso,\n" \
               "-quidve dolens, regina deum tot volvere casus\n" \
               "-insignem pietate virum, tot adire labores\n" \
               "-impulerit. Tantaene animis caelestibus irae?\n" \
               " \n"

        os.chdir(self.clone_dir)

        self._git_add_file_commit('foo.txt', FOO1, 'commit 1')

        self._gitcmd(['checkout', '-b', 'mybranch', '--track', 'master'])
        self._git_add_file_commit('foo.txt', FOO2, 'commit 2')

        self.client.get_repository_info()
        self.assertEqual(self.client.diff(None), (diff, None))
        """

    def test_diff_tracking_override(self):
        """Test GitClient diff with option override for tracking branch"""
        pass
        """
        diff = "diff --git a/foo.txt b/foo.txt\n" \
               "index 634b3e8ff85bada6f928841a9f2c505560840b3a..5e98e9540e1b741b5be24fcb33c40c1c8069c1fb 100644\n" \
               "--- a/foo.txt\n" \
               "+++ b/foo.txt\n" \
               "@@ -6,7 +6,4 @@ multa quoque et bello passus, dum conderet urbem,\n" \
               " inferretque deos Latio, genus unde Latinum,\n" \
               " Albanique patres, atque altae moenia Romae.\n" \
               " Musa, mihi causas memora, quo numine laeso,\n" \
               "-quidve dolens, regina deum tot volvere casus\n" \
               "-insignem pietate virum, tot adire labores\n" \
               "-impulerit. Tantaene animis caelestibus irae?\n" \
               " \n"

        os.chdir(self.clone_dir)
        rbtools.postreview.options.tracking = 'origin/master'

        self._gitcmd(['remote', 'add', 'bad', self.git_dir])
        self._gitcmd(['fetch', 'bad'])
        self._gitcmd(['checkout', '-b', 'mybranch', '--track', 'bad/master'])

        self._git_add_file_commit('foo.txt', FOO1, 'commit 1')

        self.client.get_repository_info()
        self.assertEqual(self.client.diff(None), (diff, None))
        """

    def test_diff_slash_tracking(self):
        """Test GitClient diff with tracking branch that has slash in its name"""
        pass
        """
        diff = "diff --git a/foo.txt b/foo.txt\n" \
               "index 5e98e9540e1b741b5be24fcb33c40c1c8069c1fb..e619c1387f5feb91f0ca83194650bfe4f6c2e347 100644\n" \
               "--- a/foo.txt\n" \
               "+++ b/foo.txt\n" \
               "@@ -1,4 +1,6 @@\n" \
               " ARMA virumque cano, Troiae qui primus ab oris\n" \
               "+ARMA virumque cano, Troiae qui primus ab oris\n" \
               "+ARMA virumque cano, Troiae qui primus ab oris\n" \
               " Italiam, fato profugus, Laviniaque venit\n" \
               " litora, multum ille et terris iactatus et alto\n" \
               " vi superum saevae memorem Iunonis ob iram;\n"

        os.chdir(self.git_dir)
        self._gitcmd(['checkout', '-b', 'not-master'])
        self._git_add_file_commit('foo.txt', FOO1, 'commit 1')

        os.chdir(self.clone_dir)
        self._gitcmd(['fetch', 'origin'])
        self._gitcmd(['checkout', '-b', 'my/branch', '--track', 'origin/not-master'])
        self._git_add_file_commit('foo.txt', FOO2, 'commit 2')

        self.client.get_repository_info()
        self.assertEqual(self.client.diff(None), (diff, None))
        """


FOO = """\
ARMA virumque cano, Troiae qui primus ab oris
Italiam, fato profugus, Laviniaque venit
litora, multum ille et terris iactatus et alto
vi superum saevae memorem Iunonis ob iram;
multa quoque et bello passus, dum conderet urbem,
inferretque deos Latio, genus unde Latinum,
Albanique patres, atque altae moenia Romae.
Musa, mihi causas memora, quo numine laeso,
quidve dolens, regina deum tot volvere casus
insignem pietate virum, tot adire labores
impulerit. Tantaene animis caelestibus irae?

"""
FOO1 = """\
ARMA virumque cano, Troiae qui primus ab oris
Italiam, fato profugus, Laviniaque venit
litora, multum ille et terris iactatus et alto
vi superum saevae memorem Iunonis ob iram;
multa quoque et bello passus, dum conderet urbem,
inferretque deos Latio, genus unde Latinum,
Albanique patres, atque altae moenia Romae.
Musa, mihi causas memora, quo numine laeso,

"""
FOO2 = """\
ARMA virumque cano, Troiae qui primus ab oris
ARMA virumque cano, Troiae qui primus ab oris
ARMA virumque cano, Troiae qui primus ab oris
Italiam, fato profugus, Laviniaque venit
litora, multum ille et terris iactatus et alto
vi superum saevae memorem Iunonis ob iram;
multa quoque et bello passus, dum conderet urbem,
inferretque deos Latio, genus unde Latinum,
Albanique patres, atque altae moenia Romae.
Musa, mihi causas memora, quo numine laeso,

"""

FOO3 = """\
ARMA virumque cano, Troiae qui primus ab oris
ARMA virumque cano, Troiae qui primus ab oris
Italiam, fato profugus, Laviniaque venit
litora, multum ille et terris iactatus et alto
vi superum saevae memorem Iunonis ob iram;
dum conderet urbem,
inferretque deos Latio, genus unde Latinum,
Albanique patres, atque altae moenia Romae.
Albanique patres, atque altae moenia Romae.
Musa, mihi causas memora, quo numine laeso,

"""
