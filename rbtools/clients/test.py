import nose
import os
import re
import shutil

from textwrap import dedent

from rbtools.clients.client import Repository
from rbtools.clients.git import GitClient
from rbtools.testutils import RBTestBase


TEST_FILE = 'foo.txt'


class GitClientTest(RBTestBase):
    def setUp(self):
        if not self.in_path('git'):
            raise nose.SkipTest('git not found in path')

        self.git = GitClient()
        self.set_user_home_tmp()

    def clone(self):
        initial = self.chdir_tmp()
        self.git.run_command(['init'])
        self.add_file(TEST_FILE, FOO)
        cloned = self.chdir_tmp()
        self.git.run_command(['clone', initial, cloned])
        return (initial, cloned)

    def add_file(self, name, content):
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
        #self.chdir_tmp()
        #self.clone()
        #repo = self.git.get_info()
        #server = self.git.scan_for_server(repo)
        #self.assertIsNone(server)
        pass

    def test_scan_for_server_reviewboardrc(self):
        "Test GitClient scan_for_server, .reviewboardrc case"""
        #os.chdir(self.clone_dir)
        #rc = open(os.path.join(self.clone_dir, '.reviewboardrc'), 'w')
        #rc.write('REVIEWBOARD_URL = "%s"' % self.TESTSERVER)
        #rc.close()

        #ri = self.client.get_repository_info()
        #server = self.client.scan_for_server(ri)
        #self.assertEqual(server, self.TESTSERVER)
        pass

    def test_scan_for_server_property(self):
        """Test GitClient scan_for_server using repo property"""
        #os.chdir(self.clone_dir)
        #self._gitcmd(['config', 'reviewboard.url', self.TESTSERVER])
        #ri = self.client.get_repository_info()

        #self.assertEqual(self.client.scan_for_server(ri), self.TESTSERVER)
        pass

    def test_diff_simple(self):
        """Test GitClient simple diff case"""
        diff = "diff --git a/foo.txt b/foo.txt\n" \
               "index 634b3e8ff85bada6f928841a9f2c505560840b3a.." \
               "5e98e9540e1b741b5be24fcb33c40c1c8069c1fb 100644\n" \
               "--- a/foo.txt\n" \
               "+++ b/foo.txt\n" \
               "@@ -6,7 +6,4 @@" \
               " multa quoque et bello passus, dum conderet urbem,\n" \
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
               "index 634b3e8ff85bada6f928841a9f2c505560840b3a.." \
               "63036ed3fcafe870d567a14dd5884f4fed70126c 100644\n" \
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
        diff1 = "diff --git a/foo.txt b/foo.txt\n" \
                "index 634b3e8ff85bada6f928841a9f2c505560840b3a.." \
                "e619c1387f5feb91f0ca83194650bfe4f6c2e347 100644\n" \
                "--- a/foo.txt\n" \
                "+++ b/foo.txt\n" \
                "@@ -1,4 +1,6 @@\n" \
                " ARMA virumque cano, Troiae qui primus ab oris\n" \
                "+ARMA virumque cano, Troiae qui primus ab oris\n" \
                "+ARMA virumque cano, Troiae qui primus ab oris\n" \
                " Italiam, fato profugus, Laviniaque venit\n" \
                " litora, multum ille et terris iactatus et alto\n" \
                " vi superum saevae memorem Iunonis ob iram;\n" \
                "@@ -6,7 +8,4 @@" \
                " multa quoque et bello passus, dum conderet urbem,\n" \
                " inferretque deos Latio, genus unde Latinum,\n" \
                " Albanique patres, atque altae moenia Romae.\n" \
                " Musa, mihi causas memora, quo numine laeso,\n" \
                "-quidve dolens, regina deum tot volvere casus\n" \
                "-insignem pietate virum, tot adire labores\n" \
                "-impulerit. Tantaene animis caelestibus irae?\n" \
                " \n"

        diff2 = "diff --git a/foo.txt b/foo.txt\n" \
                "index 634b3e8ff85bada6f928841a9f2c505560840b3a.." \
                "5e98e9540e1b741b5be24fcb33c40c1c8069c1fb 100644\n" \
                "--- a/foo.txt\n" \
                "+++ b/foo.txt\n" \
                "@@ -6,7 +6,4 @@" \
                " multa quoque et bello passus, dum conderet urbem,\n" \
                " inferretque deos Latio, genus unde Latinum,\n" \
                " Albanique patres, atque altae moenia Romae.\n" \
                " Musa, mihi causas memora, quo numine laeso,\n" \
                "-quidve dolens, regina deum tot volvere casus\n" \
                "-insignem pietate virum, tot adire labores\n" \
                "-impulerit. Tantaene animis caelestibus irae?\n" \
                " \n"

        self.clone()
        self.add_file(TEST_FILE, FOO1)
        self.git.run_command(['checkout', '-b', 'mybranch', '--track',
                             'origin/master'])
        self.add_file(TEST_FILE, FOO2)

        self.git.get_info()
        self.assertEqual(self.git.diff(None), (diff1, None))

        self.git.run_command(['checkout', 'master'])
        self.git.get_info()
        self.assertEqual(self.git.diff(None), (diff2, None))

    def test_diff_tracking_no_origin(self):
        """Test GitClient diff with a tracking branch, but no origin remote"""
        diff = "diff --git a/foo.txt b/foo.txt\n" \
               "index 634b3e8ff85bada6f928841a9f2c505560840b3a.." \
               "5e98e9540e1b741b5be24fcb33c40c1c8069c1fb 100644\n" \
               "--- a/foo.txt\n" \
               "+++ b/foo.txt\n" \
               "@@ -6,7 +6,4 @@" \
               " multa quoque et bello passus, dum conderet urbem,\n" \
               " inferretque deos Latio, genus unde Latinum,\n" \
               " Albanique patres, atque altae moenia Romae.\n" \
               " Musa, mihi causas memora, quo numine laeso,\n" \
               "-quidve dolens, regina deum tot volvere casus\n" \
               "-insignem pietate virum, tot adire labores\n" \
               "-impulerit. Tantaene animis caelestibus irae?\n" \
               " \n"

        git_dir, clone_dir = self.clone()
        self.git.run_command(['remote', 'add', 'quux', git_dir])
        self.git.run_command(['fetch', 'quux'])
        self.git.run_command(['checkout', '-b', 'mybranch', '--track',
                             'quux/master'])
        self.add_file('foo.txt', FOO1)

        self.git.get_info()
        self.assertEqual(self.git.diff(None), (diff, None))

    def test_diff_local_tracking(self):
        """Test GitClient diff with a local tracking branch"""
        diff = "diff --git a/foo.txt b/foo.txt\n" \
               "index 634b3e8ff85bada6f928841a9f2c505560840b3a.." \
               "e619c1387f5feb91f0ca83194650bfe4f6c2e347 100644\n" \
               "--- a/foo.txt\n" \
               "+++ b/foo.txt\n" \
               "@@ -1,4 +1,6 @@\n" \
               " ARMA virumque cano, Troiae qui primus ab oris\n" \
               "+ARMA virumque cano, Troiae qui primus ab oris\n" \
               "+ARMA virumque cano, Troiae qui primus ab oris\n" \
               " Italiam, fato profugus, Laviniaque venit\n" \
               " litora, multum ille et terris iactatus et alto\n" \
               " vi superum saevae memorem Iunonis ob iram;\n" \
               "@@ -6,7 +8,4 @@" \
               " multa quoque et bello passus, dum conderet urbem,\n" \
               " inferretque deos Latio, genus unde Latinum,\n" \
               " Albanique patres, atque altae moenia Romae.\n" \
               " Musa, mihi causas memora, quo numine laeso,\n" \
               "-quidve dolens, regina deum tot volvere casus\n" \
               "-insignem pietate virum, tot adire labores\n" \
               "-impulerit. Tantaene animis caelestibus irae?\n" \
               " \n"

        self.clone()
        self.add_file('foo.txt', FOO1)
        self.git.run_command(['checkout', '-b', 'mybranch', '--track',
                             'master'])
        self.add_file('foo.txt', FOO2)

        self.git.get_info()
        self.assertEqual(self.git.diff(None), (diff, None))

    def test_diff_tracking_override(self):
        """Test GitClient diff with option override for tracking branch"""
        #diff = "diff --git a/foo.txt b/foo.txt\n" \
        #       "index 634b3e8ff85bada6f928841a9f2c505560840b3a.." \
        #       "5e98e9540e1b741b5be24fcb33c40c1c8069c1fb 100644\n" \
        #       "--- a/foo.txt\n" \
        #       "+++ b/foo.txt\n" \
        #       "@@ -6,7 +6,4 @@" \
        #       " multa quoque et bello passus, dum conderet urbem,\n" \
        #       " inferretque deos Latio, genus unde Latinum,\n" \
        #       " Albanique patres, atque altae moenia Romae.\n" \
        #       " Musa, mihi causas memora, quo numine laeso,\n" \
        #       "-quidve dolens, regina deum tot volvere casus\n" \
        #       "-insignem pietate virum, tot adire labores\n" \
        #       "-impulerit. Tantaene animis caelestibus irae?\n" \
        #       " \n"

        #os.chdir(self.clone_dir)
        #rbtools.postreview.options.tracking = 'origin/master'

        #self._gitcmd(['remote', 'add', 'bad', self.git_dir])
        #self._gitcmd(['fetch', 'bad'])
        #self._gitcmd(['checkout', '-b', 'mybranch', '--track', 'bad/master'])

        #self._git_add_file_commit('foo.txt', FOO1, 'commit 1')

        #self.client.get_repository_info()
        #self.assertEqual(self.client.diff(None), (diff, None))
        pass

    def test_diff_slash_tracking(self):
        """Test GitClient diff with tracking branch"""
        """that has slash in its name"""
        diff = "diff --git a/foo.txt b/foo.txt\n" \
               "index 5e98e9540e1b741b5be24fcb33c40c1c8069c1fb.." \
               "e619c1387f5feb91f0ca83194650bfe4f6c2e347 100644\n" \
               "--- a/foo.txt\n" \
               "+++ b/foo.txt\n" \
               "@@ -1,4 +1,6 @@\n" \
               " ARMA virumque cano, Troiae qui primus ab oris\n" \
               "+ARMA virumque cano, Troiae qui primus ab oris\n" \
               "+ARMA virumque cano, Troiae qui primus ab oris\n" \
               " Italiam, fato profugus, Laviniaque venit\n" \
               " litora, multum ille et terris iactatus et alto\n" \
               " vi superum saevae memorem Iunonis ob iram;\n"

        git_dir, clone_dir = self.clone()
        os.chdir(git_dir)
        self.git.run_command(['checkout', '-b', 'not-master'])
        self.add_file('foo.txt', FOO1)

        os.chdir(clone_dir)
        self.git.run_command(['fetch', 'origin'])
        self.git.run_command(['checkout', '-b', 'my/branch', '--track',
                             'origin/not-master'])
        self.add_file('foo.txt', FOO2)

        self.git.get_info()
        self.assertEqual(self.git.diff(None), (diff, None))


class MercurialClientTest(RBTestBase):
    TESTSERVER = 'http://127.0.0.1:8080'
    CLONE_HGRC = dedent("""
    [paths]
    default = %(hg_dir)s
    cloned = %(clone_dir)s

    [reviewboard]
    url = %(test_server)s

    [diff]
    git = true
    """).rstrip()

    def add_file(self, filename, data):
        outfile = open(filename, 'w')
        outfile.write(data)
        outfile.close()
        self._hgcmd(['add', filename])
        self._hgcmd(['commit', '-m', ''])

    def setUp(self):
        #MercurialTestBase.setUp(self)
        #if not is_exe_in_path('hg'):
        #    raise nose.SkipTest('hg not found in path')

        #self.orig_dir = os.getcwd()

        #self.hg_dir = _get_tmpdir()
        #os.chdir(self.hg_dir)
        #self._hgcmd(['init'], hg_dir=self.hg_dir)
        #foo = open(os.path.join(self.hg_dir, 'foo.txt'), 'w')
        #foo.write(FOO)
        #foo.close()

        #self._hgcmd(['add', 'foo.txt'])
        #self._hgcmd(['commit', '-m', 'initial commit'])

        #self.clone_dir = _get_tmpdir()
        #os.rmdir(self.clone_dir)
        #self._hgcmd(['clone', self.hg_dir, self.clone_dir])
        #os.chdir(self.clone_dir)
        #self.client = MercurialClient()

        #clone_hgrc = open(self.clone_hgrc_path, 'wb')
        #clone_hgrc.write(self.CLONE_HGRC % {
        #    'hg_dir': self.hg_dir,
        #    'clone_dir': self.clone_dir,
        #    'test_server': self.TESTSERVER,
        #})
        #clone_hgrc.close()

        #self.client.get_repository_info()
        #rbtools.postreview.user_config = load_config_files('')
        #rbtools.postreview.options = OptionsStub()
        #rbtools.postreview.options.parent_branch = None
        #os.chdir(self.clone_dir)
        pass

    @property
    def clone_hgrc_path(self):
        return os.path.join(self.clone_dir, '.hg', 'hgrc')

    @property
    def hgrc_path(self):
        return os.path.join(self.hg_dir, '.hg', 'hgrc')

    def tearDown(self):
        #os.chdir(self.orig_dir)
        #shutil.rmtree(self.hg_dir)
        #shutil.rmtree(self.clone_dir)
        pass

    def testGetRepositoryInfoSimple(self):
        """Test MercurialClient get_repository_info, simple case"""
        #ri = self.client.get_repository_info()

        #self.assertTrue(isinstance(ri, RepositoryInfo))
        #self.assertEqual('', ri.base_path)

        #hgpath = ri.path

        #if os.path.basename(hgpath) == '.hg':
        #    hgpath = os.path.dirname(hgpath)

        #self.assertEqual(self.hg_dir, hgpath)
        #self.assertTrue(ri.supports_parent_diffs)
        #self.assertFalse(ri.supports_changesets)
        pass

    def testScanForServerSimple(self):
        """Test MercurialClient scan_for_server, simple case"""
        #os.rename(self.clone_hgrc_path,
        #    os.path.join(self.clone_dir, '._disabled_hgrc'))

        #self.client.hgrc = {}
        #self.client._load_hgrc()
        #ri = self.client.get_repository_info()

        #server = self.client.scan_for_server(ri)
        #self.assertTrue(server is None)
        pass

    def testScanForServerWhenPresentInHgrc(self):
        """Test MercurialClient scan_for_server when present in hgrc"""
        #ri = self.client.get_repository_info()

        #server = self.client.scan_for_server(ri)
        #self.assertEqual(self.TESTSERVER, server)
        pass

    def testScanForServerReviewboardrc(self):
        """Test MercurialClient scan_for_server when in .reviewboardrc"""
        #rc = open(os.path.join(self.clone_dir, '.reviewboardrc'), 'w')
        #rc.write('REVIEWBOARD_URL = "%s"' % self.TESTSERVER)
        #rc.close()

        #ri = self.client.get_repository_info()
        #server = self.client.scan_for_server(ri)
        #self.assertEqual(self.TESTSERVER, server)
        pass

    def testDiffSimple(self):
        """Test MercurialClient diff, simple case"""
        #self.client.get_repository_info()

        #self._hg_add_file_commit('foo.txt', FOO1, 'delete and modify stuff')

        #diff_result = self.client.diff(None)
        #self.assertEqual((EXPECTED_HG_DIFF_0, None), diff_result)
        pass

    def testDiffSimpleMultiple(self):
        """Test MercurialClient diff with multiple commits"""
        #self.client.get_repository_info()

        #self._hg_add_file_commit('foo.txt', FOO1, 'commit 1')
        #self._hg_add_file_commit('foo.txt', FOO2, 'commit 2')
        #self._hg_add_file_commit('foo.txt', FOO3, 'commit 3')

        #diff_result = self.client.diff(None)

        #self.assertEqual((EXPECTED_HG_DIFF_1, None), diff_result)
        pass

    def testDiffBranchDiverge(self):
        """Test MercurialClient diff with diverged branch"""
        #self._hg_add_file_commit('foo.txt', FOO1, 'commit 1')

        #self._hgcmd(['branch', 'diverged'])
        #self._hg_add_file_commit('foo.txt', FOO2, 'commit 2')
        #self.client.get_repository_info()

        #self.assertEqual((EXPECTED_HG_DIFF_2, None), self.client.diff(None))

        #self._hgcmd(['update', '-C', 'default'])
        #self.client.get_repository_info()

        #self.assertEqual((EXPECTED_HG_DIFF_3, None), self.client.diff(None))
        pass


class MercurialSubversionClientTest(MercurialClientTest):
    def setUp(self):
        #self._tmpbase = ''
        #self.clone_dir = ''
        #self.svn_repo = ''
        #self.svn_checkout = ''
        #self.client = None
        #self._svnserve_pid = 0
        #self._max_svnserve_pid_tries = 12
        #self._svnserve_port = os.environ.get('SVNSERVE_PORT')
        #self._required_exes = ('svnadmin', 'svnserve', 'svn')
        #super(MercurialSubversionClientTest, self).setUp()
        #self._hg_env = {'FOO': 'BAR'}

        #for exe in self._required_exes:
        #    if not is_exe_in_path(exe):
        #        raise nose.SkipTest('missing svn stuff!  giving up!')

        #if not self._has_hgsubversion():
        #    raise nose.SkipTest('unable to use `hgsubversion` extension!  '
        #                        'giving up!')

        #if not self._tmpbase:
        #    self._tmpbase = _get_tmpdir()

        #self._create_svn_repo()
        #self._fire_up_svnserve()
        #self._fill_in_svn_repo()

        #try:
        #    self._get_testing_clone()
        #except (OSError, IOError):
        #    msg = 'could not clone from svn repo!  skipping...'
        #    raise nose.SkipTest(msg), None, sys.exc_info()[2]

        #self._spin_up_client()
        #self._stub_in_config_and_options()
        #os.chdir(self.clone_dir)
        pass

    def _has_hgsubversion(self):
        output = self._hgcmd(['svn', '--help'],
                             ignore_errors=True, extra_ignore_errors=(255))

        return not re.search("unknown command ['\"]svn['\"]", output, re.I)

    def tearDown(self):
        #shutil.rmtree(self.clone_dir)
        #os.kill(self._svnserve_pid, 9)

        #if self._tmpbase:
        #    shutil.rmtree(self._tmpbase)
        pass

    def _svn_add_file_commit(self, filename, data, msg):
        #outfile = open(filename, 'w')
        #outfile.write(data)
        #outfile.close()
        #execute(['svn', 'add', filename])
        #execute(['svn', 'commit', '-m', msg])
        pass

    def _create_svn_repo(self):
        #self.svn_repo = os.path.join(self._tmpbase, 'svnrepo')
        #execute(['svnadmin', 'create', self.svn_repo])
        pass

    def _fire_up_svnserve(self):
        #if not self._svnserve_port:
        #    self._svnserve_port = str(randint(30000, 40000))

        #pid_file = os.path.join(self._tmpbase, 'svnserve.pid')
        #execute(['svnserve', '--pid-file', pid_file, '-d',
        #         '--listen-port', self._svnserve_port, '-r', self._tmpbase])

        #for i in range(0, self._max_svnserve_pid_tries):
        #    try:
        #        self._svnserve_pid = int(open(pid_file).read().strip())
        #        return

        #    except (IOError, OSError):
        #        time.sleep(0.25)

        ## This will re-raise the last exception, which will be either
        ## IOError or OSError if the above fails and this branch is reached
        #raise
        pass

    def _fill_in_svn_repo(self):
        #self.svn_checkout = os.path.join(self._tmpbase, 'checkout.svn')
        #execute(['svn', 'checkout', 'file://%s' % self.svn_repo,
        #         self.svn_checkout])
        #os.chdir(self.svn_checkout)

        #for subtree in ('trunk', 'branches', 'tags'):
        #    execute(['svn', 'mkdir', subtree])

        #execute(['svn', 'commit', '-m', 'filling in T/b/t'])
        #os.chdir(os.path.join(self.svn_checkout, 'trunk'))

        #for i, data in enumerate([FOO, FOO1, FOO2]):
        #    self._svn_add_file_commit('foo.txt', data, 'foo commit %s' % i)
        pass

    def _get_testing_clone(self):
        #self.clone_dir = os.path.join(self._tmpbase, 'checkout.hg')
        #self._hgcmd([
        #    'clone', 'svn://127.0.0.1:%s/svnrepo' % self._svnserve_port,
        #    self.clone_dir,
        #])
        pass

    def _spin_up_client(self):
        #os.chdir(self.clone_dir)
        #self.client = MercurialClient()
        pass

    def _stub_in_config_and_options(self):
        #rbtools.postreview.user_config = load_config_files('')
        #rbtools.postreview.options = OptionsStub()
        #rbtools.postreview.options.parent_branch = None
        pass

    def testGetRepositoryInfoSimple(self):
        """Test MercurialClient (+svn) get_repository_info, simple case"""
        #ri = self.client.get_repository_info()

        #self.assertEqual('svn', self.client._type)
        #self.assertEqual('/trunk', ri.base_path)
        #self.assertEqual('svn://127.0.0.1:%s/svnrepo' % self._svnserve_port,
        #                ri.path)
        pass

    def testScanForServerSimple(self):
        """Test MercurialClient (+svn) scan_for_server, simple case"""
        #ri = self.client.get_repository_info()
        #server = self.client.scan_for_server(ri)

        #self.assertTrue(server is None)
        pass

    def testScanForServerReviewboardrc(self):
        """Test MercurialClient (+svn) scan_for_server in .reviewboardrc"""
        #rc_filename = os.path.join(self.clone_dir, '.reviewboardrc')
        #rc = open(rc_filename, 'w')
        #rc.write('REVIEWBOARD_URL = "%s"' % self.TESTSERVER)
        #rc.close()

        #ri = self.client.get_repository_info()
        #server = self.client.scan_for_server(ri)

        #self.assertEqual(self.TESTSERVER, server)
        pass

    def testScanForServerProperty(self):
        """Test MercurialClient (+svn) scan_for_server in svn property"""
        #os.chdir(self.svn_checkout)
        #execute(['svn', 'update'])
        #execute(['svn', 'propset', 'reviewboard:url', self.TESTSERVER,
        #         self.svn_checkout])
        #execute(['svn', 'commit', '-m', 'adding reviewboard:url property'])

        #os.chdir(self.clone_dir)
        #self._hgcmd(['pull'])
        #self._hgcmd(['update', '-C'])

        #ri = self.client.get_repository_info()

        #self.assertEqual(self.TESTSERVER, self.client.scan_for_server(ri))
        pass

    def testDiffSimple(self):
        """Test MercurialClient (+svn) diff, simple case"""
        #self.client.get_repository_info()

        #self._hg_add_file_commit('foo.txt', FOO4, 'edit 4')

        #self.assertEqual(EXPECTED_HG_SVN_DIFF_0, self.client.diff(None)[0])
        pass

    def testDiffSimpleMultiple(self):
        """Test MercurialClient (+svn) diff with multiple commits"""
        #self.client.get_repository_info()

        #self._hg_add_file_commit('foo.txt', FOO4, 'edit 4')
        #self._hg_add_file_commit('foo.txt', FOO5, 'edit 5')
        #self._hg_add_file_commit('foo.txt', FOO6, 'edit 6')

        #self.assertEqual(EXPECTED_HG_SVN_DIFF_1, self.client.diff(None)[0])
        pass


class SVNClientTests(RBTestBase):
    def test_relative_paths(self):
        """Testing SvnRepositoryInfo._get_relative_path"""
        #info = SVNRepository('http://svn.example.com/svn/', '/', '')
        #self.assertEqual(info._get_relative_path('/foo', '/bar'), None)
        #self.assertEqual(info._get_relative_path('/', '/trunk/myproject'),
        #                 None)
        #self.assertEqual(info._get_relative_path('/trunk/myproject', '/'),
        #                 '/trunk/myproject')
        #self.assertEqual(
        #    info._get_relative_path('/trunk/myproject', ''),
        #    '/trunk/myproject')
        #self.assertEqual(
        #    info._get_relative_path('/trunk/myproject', '/trunk'),
        #    '/myproject')
        #self.assertEqual(
        #    info._get_relative_path('/trunk/myproject', '/trunk/myproject'),
        #    '/')
        pass


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

FOO4 = """\
Italiam, fato profugus, Laviniaque venit
litora, multum ille et terris iactatus et alto
vi superum saevae memorem Iunonis ob iram;
dum conderet urbem,





inferretque deos Latio, genus unde Latinum,
Albanique patres, atque altae moenia Romae.
Musa, mihi causas memora, quo numine laeso,

"""

FOO5 = """\
litora, multum ille et terris iactatus et alto
Italiam, fato profugus, Laviniaque venit
vi superum saevae memorem Iunonis ob iram;
dum conderet urbem,
Albanique patres, atque altae moenia Romae.
Albanique patres, atque altae moenia Romae.
Musa, mihi causas memora, quo numine laeso,
inferretque deos Latio, genus unde Latinum,

ARMA virumque cano, Troiae qui primus ab oris
ARMA virumque cano, Troiae qui primus ab oris
"""

FOO6 = """\
ARMA virumque cano, Troiae qui primus ab oris
ARMA virumque cano, Troiae qui primus ab oris
Italiam, fato profugus, Laviniaque venit
litora, multum ille et terris iactatus et alto
vi superum saevae memorem Iunonis ob iram;
dum conderet urbem, inferretque deos Latio, genus
unde Latinum, Albanique patres, atque altae
moenia Romae. Albanique patres, atque altae
moenia Romae. Musa, mihi causas memora, quo numine laeso,

"""

EXPECTED_HG_DIFF_0 = """\
diff --git a/foo.txt b/foo.txt
--- a/foo.txt
+++ b/foo.txt
@@ -6,7 +6,4 @@
 inferretque deos Latio, genus unde Latinum,
 Albanique patres, atque altae moenia Romae.
 Musa, mihi causas memora, quo numine laeso,
-quidve dolens, regina deum tot volvere casus
-insignem pietate virum, tot adire labores
-impulerit. Tantaene animis caelestibus irae?
 
"""

EXPECTED_HG_DIFF_1 = """\
diff --git a/foo.txt b/foo.txt
--- a/foo.txt
+++ b/foo.txt
@@ -1,12 +1,11 @@
+ARMA virumque cano, Troiae qui primus ab oris
 ARMA virumque cano, Troiae qui primus ab oris
 Italiam, fato profugus, Laviniaque venit
 litora, multum ille et terris iactatus et alto
 vi superum saevae memorem Iunonis ob iram;
-multa quoque et bello passus, dum conderet urbem,
+dum conderet urbem,
 inferretque deos Latio, genus unde Latinum,
 Albanique patres, atque altae moenia Romae.
+Albanique patres, atque altae moenia Romae.
 Musa, mihi causas memora, quo numine laeso,
-quidve dolens, regina deum tot volvere casus
-insignem pietate virum, tot adire labores
-impulerit. Tantaene animis caelestibus irae?
 
"""

EXPECTED_HG_DIFF_2 = """\
diff --git a/foo.txt b/foo.txt
--- a/foo.txt
+++ b/foo.txt
@@ -1,3 +1,5 @@
+ARMA virumque cano, Troiae qui primus ab oris
+ARMA virumque cano, Troiae qui primus ab oris
 ARMA virumque cano, Troiae qui primus ab oris
 Italiam, fato profugus, Laviniaque venit
 litora, multum ille et terris iactatus et alto
"""

EXPECTED_HG_DIFF_3 = """\
diff --git a/foo.txt b/foo.txt
--- a/foo.txt
+++ b/foo.txt
@@ -6,7 +6,4 @@
 inferretque deos Latio, genus unde Latinum,
 Albanique patres, atque altae moenia Romae.
 Musa, mihi causas memora, quo numine laeso,
-quidve dolens, regina deum tot volvere casus
-insignem pietate virum, tot adire labores
-impulerit. Tantaene animis caelestibus irae?
 
"""

EXPECTED_HG_SVN_DIFF_0 = """\
Index: foo.txt
===================================================================
--- foo.txt\t(revision 4)
+++ foo.txt\t(working copy)
@@ -1,4 +1,1 @@
-ARMA virumque cano, Troiae qui primus ab oris
-ARMA virumque cano, Troiae qui primus ab oris
-ARMA virumque cano, Troiae qui primus ab oris
 Italiam, fato profugus, Laviniaque venit
@@ -6,3 +3,8 @@
 vi superum saevae memorem Iunonis ob iram;
-multa quoque et bello passus, dum conderet urbem,
+dum conderet urbem,
+
+
+
+
+
 inferretque deos Latio, genus unde Latinum,
"""

EXPECTED_HG_SVN_DIFF_1 = """\
Index: foo.txt
===================================================================
--- foo.txt\t(revision 4)
+++ foo.txt\t(working copy)
@@ -1,2 +1,1 @@
-ARMA virumque cano, Troiae qui primus ab oris
 ARMA virumque cano, Troiae qui primus ab oris
@@ -6,6 +5,6 @@
 vi superum saevae memorem Iunonis ob iram;
-multa quoque et bello passus, dum conderet urbem,
-inferretque deos Latio, genus unde Latinum,
-Albanique patres, atque altae moenia Romae.
-Musa, mihi causas memora, quo numine laeso,
+dum conderet urbem, inferretque deos Latio, genus
+unde Latinum, Albanique patres, atque altae
+moenia Romae. Albanique patres, atque altae
+moenia Romae. Musa, mihi causas memora, quo numine laeso,
 
"""
