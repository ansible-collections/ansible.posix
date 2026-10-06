from __future__ import absolute_import, division, print_function

__metaclass__ = type

'''
(Epdb) pprint(DeepDiff(self.final_task_vars, out_task_vars), indent=2)
{ 'dic_item_added': set([u"root['ansible_python_interpreter']"]),
  'dic_item_removed': set([ u"root['hostvars']['127.0.0.1']",
                            u"root['hostvars']['::1']",
                            u"root['hostvars']['localhost']"]),
  'iterable_item_added': { u"root['hostvars']['el6host']['groups']['all'][1]": u'::1',
                           u"root['hostvars']['el6host']['groups']['ungrouped'][1]": u'::1',
                           u"root['vars']['hostvars']['el6host']['groups']['all'][1]": u'::1',
                           u"root['vars']['hostvars']['el6host']['groups']['ungrouped'][1]": u'::1'}}
'''

import errno
import json
import os
import shutil
import stat
import tempfile
import unittest
import yaml
from collections import namedtuple

from ansible import constants as C
from ansible.errors import AnsibleError
from ansible.parsing.dataloader import DataLoader
from ansible.parsing.vault import VaultLib, VaultSecret
from ansible_collections.ansible.posix.tests.unit.compat.mock import patch, MagicMock
from ansible_collections.ansible.posix.plugins.action.synchronize import ActionModule


# Getting the incoming and outgoing task vars from the plugin's run method

'''
import copy
safe_vars = {}
for k,v in task_vars.items():
    if k not in ['vars', 'hostvars']:
        safe_vars[k] = copy.deepcopy(v)
    else:
        sdata = str(v)
        newv = eval(sdata)
        safe_vars[k] = newv

import json
with open('task_vars.json', 'wb') as f:
    f.write(json.dumps(safe_vars, indent=2))
'''


class BreakPoint(Exception):
    pass


class TaskMock(object):
    args = {'src': u'/tmp/deleteme',
            'dest': '/tmp/deleteme',
            'rsync_path': 'rsync'}
    async_val = None
    become = None
    become_user = None
    become_method = None
    check_mode = False
    delegate_to = None
    diff = False
    no_log = None


class StdinMock(object):
    shell = None


class ConnectionMock(object):
    ismock = True
    _play_context = None
    always_pipeline_modules = False
    become = None
    has_pipelining = False
    socket_path = None
    # transport = 'ssh'
    transport = None
    _new_stdin = StdinMock()

    get_option = MagicMock(return_value='root')

    # my shell
    _shell = MagicMock()
    _shell.mkdtemp.return_value = 'mkdir command'
    _shell.join_path.side_effect = os.path.join
    _shell.get_option = MagicMock(return_value=['root', 'toor'])


class PlayContextMock(object):
    shell = None
    private_key_file = None
    become = False
    become_user = 'root'
    become_method = None
    check_mode = False
    no_log = None
    diff = None
    remote_addr = None
    remote_user = None
    password = None


class ModuleLoaderMock(object):
    def find_plugin(self, module_name, mod_type):
        pass


class SharedLoaderMock(object):
    module_loader = ModuleLoaderMock()


class SynchronizeTester(object):

    ''' A wrapper for mocking out synchronize environments '''

    task = TaskMock()
    connection = ConnectionMock()
    _play_context = PlayContextMock()
    loader = None
    templar = None
    shared_loader_obj = SharedLoaderMock()

    final_task_vars = None
    execute_called = False

    def _execute_module(self, module_name, module_args=None, task_vars=None):
        self.execute_called = True
        self.final_module_args = module_args
        self.final_task_vars = task_vars
        return {}

    def runtest(self, fixturepath='fixtures/synchronize/basic'):
        # Reset task and connection to avoid state leaking between tests
        self.task = TaskMock()
        self.connection = ConnectionMock()

        metapath = os.path.join(fixturepath, 'meta.yaml')
        with open(metapath, 'rb') as f:
            fdata = f.read()
        test_meta = yaml.safe_load(fdata)

        # load initial play context vars
        if '_play_context' in test_meta:
            if test_meta['_play_context']:
                self.task.args = {}
                for (k, v) in test_meta['_play_context'].items():
                    if v == 'None':
                        v = None
                    setattr(self._play_context, k, v)

        # load initial task context vars
        if '_task' in test_meta:
            if test_meta['_task']:
                self.task.args = {}
                for (k, v) in test_meta['_task'].items():
                    # import epdb; epdb.st()
                    if v == 'None':
                        v = None
                    setattr(self.task, k, v)

        # load initial task vars
        if 'task_args' in test_meta:
            if test_meta['task_args']:
                self.task.args = {}
                for (k, v) in test_meta['task_args'].items():
                    self.task.args[k] = v

        # load initial task vars
        invarspath = os.path.join(fixturepath, test_meta.get('fixtures', {}).get('taskvars_in', 'taskvars_in.json'))
        with open(invarspath, 'rb') as f:
            fdata = f.read()
        fdata = fdata.decode("utf-8")
        in_task_vars = json.loads(fdata)

        # load expected final task vars
        outvarspath = os.path.join(fixturepath, test_meta.get('fixtures', {}).get('taskvars_out', 'taskvars_out.json'))
        with open(outvarspath, 'rb') as f:
            fdata = f.read()
        fdata = fdata.decode("utf-8")
        out_task_vars = json.loads(fdata)

        # fixup the connection
        for (k, v) in test_meta['connection'].items():
            setattr(self.connection, k, v)

        # fixup the hostvars
        if test_meta['hostvars']:
            for (k, v) in test_meta['hostvars'].items():
                in_task_vars['hostvars'][k] = v

        # initialize and run the module
        SAM = ActionModule(self.task, self.connection, self._play_context,
                           self.loader, self.templar, self.shared_loader_obj)
        SAM._execute_module = self._execute_module
        result = SAM.run(task_vars=in_task_vars)

        # run assertions
        for check in test_meta['asserts']:
            value = eval(check)
            # if not value:
            #     print(check, value)
            #     import epdb; epdb.st()
            assert value, check


class FakePluginLoader(object):
    mocked = True

    @staticmethod
    def get(transport, play_context, new_stdin):
        conn = ConnectionMock()
        conn.transport = transport
        conn._play_context = play_context
        conn._new_stdin = new_stdin
        return conn


class TestSynchronizeAction(unittest.TestCase):

    fixturedir = os.path.dirname(__file__)
    fixturedir = os.path.join(fixturedir, 'fixtures', 'synchronize')
    # print(basedir)

    @patch('ansible_collections.ansible.posix.plugins.action.synchronize.connection_loader', FakePluginLoader)
    def test_basic(self):
        x = SynchronizeTester()
        x.runtest(fixturepath=os.path.join(self.fixturedir, 'basic'))

    @patch('ansible_collections.ansible.posix.plugins.action.synchronize.connection_loader', FakePluginLoader)
    def test_ansible_host_from_task_vars(self):
        # ansible_host set only via play-level vars (present in top-level
        # task_vars, absent from the hostvars snapshot for the target host)
        # must still be used to build the rsync destination.
        # Regression test for https://github.com/ansible-collections/ansible.posix/issues/469
        x = SynchronizeTester()
        x.runtest(fixturepath=os.path.join(self.fixturedir, 'ansible_host_from_task_vars'))

    @patch('ansible_collections.ansible.posix.plugins.action.synchronize.connection_loader', FakePluginLoader)
    def test_basic_become(self):
        x = SynchronizeTester()
        x.runtest(fixturepath=os.path.join(self.fixturedir, 'basic_become'))

    @patch('ansible_collections.ansible.posix.plugins.action.synchronize.connection_loader', FakePluginLoader)
    def test_basic_become_cli(self):
        # --become on the cli sets _play_context.become
        x = SynchronizeTester()
        x.runtest(fixturepath=os.path.join(self.fixturedir, 'basic_become_cli'))

    @patch('ansible_collections.ansible.posix.plugins.action.synchronize.connection_loader', FakePluginLoader)
    def test_basic_vagrant(self):
        # simple vagrant example
        x = SynchronizeTester()
        x.runtest(fixturepath=os.path.join(self.fixturedir, 'basic_vagrant'))

    @patch('ansible_collections.ansible.posix.plugins.action.synchronize.connection_loader', FakePluginLoader)
    def test_basic_vagrant_sudo(self):
        # vagrant plus sudo
        x = SynchronizeTester()
        x.runtest(fixturepath=os.path.join(self.fixturedir, 'basic_vagrant_sudo'))

    @patch('ansible_collections.ansible.posix.plugins.action.synchronize.connection_loader', FakePluginLoader)
    def test_basic_vagrant_become_cli(self):
        # vagrant plus sudo
        x = SynchronizeTester()
        x.runtest(fixturepath=os.path.join(self.fixturedir, 'basic_vagrant_become_cli'))

    @patch('ansible_collections.ansible.posix.plugins.action.synchronize.connection_loader', FakePluginLoader)
    def test_delegate_remote(self):
        # delegate to other remote host
        x = SynchronizeTester()
        x.runtest(fixturepath=os.path.join(self.fixturedir, 'delegate_remote'))

    @patch('ansible_collections.ansible.posix.plugins.action.synchronize.connection_loader', FakePluginLoader)
    def test_delegate_remote_su(self):
        # delegate to other remote host with su enabled
        x = SynchronizeTester()
        x.runtest(fixturepath=os.path.join(self.fixturedir, 'delegate_remote_su'))

    @patch('ansible_collections.ansible.posix.plugins.action.synchronize.connection_loader', FakePluginLoader)
    def test_basic_with_private_key(self):
        x = SynchronizeTester()
        x.runtest(fixturepath=os.path.join(self.fixturedir, 'basic_with_private_key'))

    @patch('ansible_collections.ansible.posix.plugins.action.synchronize.connection_loader', FakePluginLoader)
    def test_delegate_remote_with_private_key(self):
        # delegate to other remote host and use the module param private_key
        x = SynchronizeTester()
        x.runtest(fixturepath=os.path.join(self.fixturedir, 'delegate_remote_with_private_key'))

    @patch('ansible_collections.ansible.posix.plugins.action.synchronize.connection_loader', FakePluginLoader)
    def test_delegate_remote_play_context_private_key(self):
        # delegate to other remote host and use the play context private_key
        x = SynchronizeTester()
        x.runtest(fixturepath=os.path.join(self.fixturedir, 'delegate_remote_play_context_private_key'))

    @patch.object(ActionModule, '_low_level_execute_command', side_effect=BreakPoint)
    @patch.object(ActionModule, '_remote_expand_user', side_effect=ActionModule._remote_expand_user, autospec=True)
    def test_remote_user_not_in_local_tmpdir(self, spy_remote_expand_user, ll_ec):
        x = SynchronizeTester()
        SAM = ActionModule(x.task, x.connection, x._play_context,
                           x.loader, x.templar, x.shared_loader_obj)
        try:
            SAM.run(task_vars={'hostvars': {'foo': {}, 'localhost': {}}, 'inventory_hostname': 'foo'})
        except BreakPoint:
            pass
        self.assertEqual(spy_remote_expand_user.call_count, 0)


class DecryptTester(SynchronizeTester):

    ''' Runs the action plugin on the basic fixture with the given loader and records the staged source '''

    def __init__(self, loader, execute_side_effect=None):
        self.task = TaskMock()
        self.connection = ConnectionMock()
        self._play_context = PlayContextMock()
        self.loader = loader
        self.execute_side_effect = execute_side_effect
        self.final_module_args = None
        self.staging_dir = None
        self.staging_dir_mode = None
        self.staged = None
        self.staged_parents = None
        self.staged_parent_names = None

    def _execute_module(self, module_name, module_args=None, task_vars=None):
        self.execute_called = True
        self.final_module_args = module_args
        src = module_args['src']
        if src.startswith(C.DEFAULT_LOCAL_TMP + '/'):
            self.staging_dir = os.path.join(C.DEFAULT_LOCAL_TMP, src[len(C.DEFAULT_LOCAL_TMP) + 1:].split('/')[0])
            self.staging_dir_mode = stat.S_IMODE(os.stat(self.staging_dir).st_mode)
            staged_path = strip_content_form(src)
            self.staged = snapshot(staged_path)
            self.staged_parents = {}
            self.staged_parent_names = {}
            parent = staged_path
            while not os.path.samefile(parent, self.staging_dir):
                parent = os.path.dirname(parent)
                real_parent = os.path.realpath(parent)[len(self.staging_dir):] or '/'
                self.staged_parents[real_parent] = list(snapshot(parent, recurse=False).values())[0]
                self.staged_parent_names[real_parent] = os.listdir(parent)
        if self.execute_side_effect is not None:
            raise self.execute_side_effect
        return {}

    def run(self, task_args, transport='ssh', delegate_to=None, check_mode=False, task_vars=None):
        fixturepath = os.path.join(os.path.dirname(__file__), 'fixtures', 'synchronize', 'basic')
        with open(os.path.join(fixturepath, 'taskvars_in.json'), 'rb') as f:
            in_task_vars = json.loads(f.read().decode('utf-8'))
        for host in ('127.0.0.1', '::1', 'localhost'):
            in_task_vars['hostvars'][host] = {}
        in_task_vars.update(task_vars or {})

        self.task.args = task_args
        self.task.delegate_to = delegate_to
        self.task.check_mode = check_mode
        self._play_context.check_mode = check_mode
        self.connection.transport = transport

        SAM = ActionModule(self.task, self.connection, self._play_context,
                           self.loader, self.templar, self.shared_loader_obj)
        SAM._execute_module = self._execute_module
        return SAM.run(task_vars=in_task_vars)


Entry = namedtuple('Entry', ['data', 'target_data', 'mode', 'mtime', 'ino', 'nlink'])


def strip_content_form(path):
    while path.endswith('/') or path.endswith('/.'):
        path = path[:-1]
    return path


def snapshot(path, recurse=True):
    ''' Returns an Entry for path and everything below it, keyed by the path relative to the parent directory of path '''
    paths = [path]
    if recurse and not os.path.islink(path):
        for root, dirs, files in os.walk(path):
            paths.extend(os.path.join(root, name) for name in dirs + files)

    found = {}
    for item in paths:
        st = os.lstat(item)
        data = target_data = None
        if stat.S_ISLNK(st.st_mode):
            data = os.readlink(item)
            if os.path.isfile(item):
                with open(item, 'rb') as f:
                    target_data = f.read()
        elif stat.S_ISREG(st.st_mode) and os.access(item, os.R_OK):
            with open(item, 'rb') as f:
                data = f.read()
        found[os.path.relpath(item, os.path.dirname(path))] = Entry(data, target_data, st.st_mode, st.st_mtime_ns, st.st_ino, st.st_nlink)
    return found


@patch('ansible_collections.ansible.posix.plugins.action.synchronize.connection_loader', FakePluginLoader)
class TestSynchronizeDecrypt(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.secrets = [('default', VaultSecret(b'synchronize'))]
        vault = VaultLib(cls.secrets)
        cls.top_secret = vault.encrypt(b'top secret\n')
        cls.deep_secret = vault.encrypt(b'deep secret\n')
        cls.other_secret = VaultLib([('default', VaultSecret(b'other'))]).encrypt(b'other secret\n')

    def setUp(self):
        self.tmpdir = os.path.realpath(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.tmpdir, True)

        self.local_tmp = os.path.join(self.tmpdir, 'local_tmp')
        os.mkdir(self.local_tmp)
        patcher = patch.object(C, 'DEFAULT_LOCAL_TMP', self.local_tmp)
        patcher.start()
        self.addCleanup(patcher.stop)

        self.loader = DataLoader()
        self.loader.set_vault_secrets(self.secrets)
        self.loader.get_real_file = MagicMock(wraps=self.loader.get_real_file)

        self.parent = os.path.join(self.tmpdir, 'etc')
        self.src = os.path.join(self.parent, 'conf.d')
        os.makedirs(os.path.join(self.src, 'sub', 'deep'))
        os.mkdir(os.path.join(self.src, 'plain_only'))
        os.mkdir(os.path.join(self.src, 'empty'))
        self._write('plain.txt', b'plain\n', 0o644, 1500000000)
        self._write('plain_only/plain.txt', b'plain only\n', 0o640, 1500000001)
        self._write('sub/plain.txt', b'sub plain\n', 0o444, 1500000002)
        dirs = (('sub/deep', 0o755), ('sub', 0o750), ('plain_only', 0o700), ('empty', 0o775), ('', 0o755), ('..', 0o751))
        for number, (name, mode) in enumerate(dirs):
            os.chmod(os.path.join(self.src, name), mode)
            os.utime(os.path.join(self.src, name), (1500000010 + number, 1500000010 + number))

    def _write(self, name, data, mode, mtime):
        path = os.path.join(self.src, name)
        times = os.stat(os.path.dirname(path))
        with open(path, 'wb') as f:
            f.write(data)
        os.chmod(path, mode)
        os.utime(path, (mtime, mtime))
        os.utime(os.path.dirname(path), ns=(times.st_atime_ns, times.st_mtime_ns))
        return path

    def _symlink(self, target, name, mtime=1400000010):
        path = os.path.join(self.src, name)
        times = os.stat(os.path.dirname(path))
        os.symlink(target, path)
        os.utime(path, (mtime, mtime), follow_symlinks=False)
        os.utime(os.path.dirname(path), ns=(times.st_atime_ns, times.st_mtime_ns))
        return path

    def _encrypt(self):
        self._write('secret.yml', self.top_secret, 0o600, 1400000000)
        self._write('sub/deep/key.pem', self.deep_secret, 0o640, 1400000001)

    def _args(self, **kwargs):
        args = {'src': self.src, 'dest': '/tmp/deleteme'}
        args.update(kwargs)
        return args

    def _decrypted_paths(self):
        return [call[0][0] for call in self.loader.get_real_file.call_args_list]

    def _outside_local_tmp(self):
        ''' Returns the snapshot of everything the test created outside of the local temporary directory '''
        found = {}
        for name in os.listdir(self.tmpdir):
            if name != 'local_tmp':
                found.update(snapshot(os.path.join(self.tmpdir, name)))
        return found

    def _assert_clean(self):
        self.assertEqual(os.listdir(self.local_tmp), [])

    def _assert_staged_src(self, x, src):
        self.assertEqual(os.path.dirname(x.staging_dir), self.local_tmp)
        self.assertEqual(x.staging_dir_mode, 0o700)
        if '/./' in src:
            self.assertEqual(x.final_module_args['src'], x.staging_dir + src)
        else:
            self.assertEqual(x.final_module_args['src'], x.staging_dir + '/.' + src)

    def _assert_staged_tree(self, staged, name='conf.d', decrypted=None, copied=()):
        ''' staged has to mirror self.src with decrypted copies of the encrypted files and hard links to the other files '''
        if decrypted is None:
            decrypted = {'secret.yml': b'top secret\n', 'sub/deep/key.pem': b'deep secret\n'}
        original = snapshot(self.src)
        self.assertEqual(sorted(staged), sorted(name + key[len('conf.d'):] for key in original))
        for key in original:
            real = original[key]
            mirrored = staged[name + key[len('conf.d'):]]
            relative = key[len('conf.d/'):]
            self.assertEqual(mirrored.mode, real.mode, key)
            self.assertEqual(mirrored.mtime, real.mtime, key)
            if relative in decrypted:
                self.assertEqual(mirrored.data, decrypted[relative], key)
                self.assertNotEqual(mirrored.ino, real.ino, key)
                self.assertEqual((mirrored.nlink, real.nlink), (1, 1), key)
            elif stat.S_ISDIR(real.mode) or stat.S_ISLNK(real.mode) or relative in copied:
                self.assertEqual(mirrored.data, real.data, key)
                self.assertNotEqual(mirrored.ino, real.ino, key)
            else:
                self.assertEqual(mirrored.ino, real.ino, key)
                self.assertEqual(mirrored.nlink, 2, key)

    def _assert_refused(self, x, result, msg='decrypt'):
        self.assertTrue(result.get('failed'))
        self.assertIn(msg, result['msg'])
        self.assertFalse(x.execute_called)
        self.assertEqual(self._decrypted_paths(), [])
        self._assert_clean()

    def test_decrypt_unset_or_false_changes_nothing(self):
        self._encrypt()
        final_args = []
        for args in (self._args(), self._args(decrypt=False), self._args(decrypt='no')):
            loader = MagicMock()
            x = DecryptTester(loader)
            with patch.object(tempfile, 'mkdtemp', side_effect=AssertionError('staging')):
                result = x.run(args)
            self.assertFalse(result.get('failed'))
            self.assertEqual(loader.mock_calls, [])
            self._assert_clean()
            x.final_module_args.pop('decrypt', None)
            final_args.append(x.final_module_args)
        self.assertEqual(final_args[0], final_args[1])
        self.assertEqual(final_args[0], final_args[2])
        self.assertEqual(final_args[0]['src'], self.src)

    def test_decrypt_unset_works_without_loader(self):
        x = DecryptTester(None)
        result = x.run(self._args())
        self.assertFalse(result.get('failed'))
        self.assertTrue(x.execute_called)

    def test_decrypt_without_encrypted_files_does_not_stage(self):
        for src in (self.src, self.src + '/', os.path.join(self.src, 'plain.txt'), os.path.join(self.src, 'missing')):
            expected = DecryptTester(None)
            expected.run(self._args(src=src))
            x = DecryptTester(self.loader)
            with patch.object(tempfile, 'mkdtemp', side_effect=AssertionError('staging')), \
                    patch.object(os, 'link', side_effect=AssertionError('staging')):
                result = x.run(self._args(src=src, decrypt=True))
            self.assertFalse(result.get('failed'))
            self.assertTrue(x.execute_called)
            self.assertIs(x.final_module_args.pop('decrypt'), True)
            self.assertEqual(x.final_module_args, expected.final_module_args)
            self.assertEqual(x.final_module_args['src'], src)
            self.assertEqual(self._decrypted_paths(), [])
            self._assert_clean()

    def test_decrypt_directory(self):
        self._encrypt()
        os.mkfifo(os.path.join(self.src, 'sub', 'fifo'))
        os.utime(os.path.join(self.src, 'sub'), (1500000011, 1500000011))
        before = self._outside_local_tmp()

        x = DecryptTester(self.loader)
        result = x.run(self._args(decrypt=True))
        self.assertFalse(result.get('failed'), result.get('msg'))
        self._assert_staged_src(x, self.src)
        self.assertEqual(sorted(self._decrypted_paths()),
                         [os.path.join(self.src, 'secret.yml'), os.path.join(self.src, 'sub', 'deep', 'key.pem')])
        self._assert_staged_tree(x.staged)
        self.assertEqual(x.staged['conf.d/plain.txt'].data, b'plain\n')
        self.assertEqual(x.staged['conf.d/plain_only/plain.txt'].data, b'plain only\n')
        self.assertTrue(stat.S_ISDIR(x.staged['conf.d/empty'].mode))
        self.assertTrue(stat.S_ISFIFO(x.staged['conf.d/sub/fifo'].mode))
        self.assertEqual(stat.S_IMODE(x.staged['conf.d/secret.yml'].mode), 0o600)
        self.assertEqual(x.staged['conf.d/secret.yml'].mtime, 1400000000 * 10 ** 9)
        self.assertEqual(stat.S_IMODE(x.staged['conf.d/sub'].mode), 0o750)
        self.assertEqual(x.staged['conf.d/sub'].mtime, 1500000011 * 10 ** 9)
        self._assert_clean()
        self.assertEqual(self._outside_local_tmp(), before)

    def test_decrypt_source_path_mapping(self):
        self._encrypt()
        os.symlink(self.parent, os.path.join(self.tmpdir, 'link'))
        srcs = [(self.src + suffix, self.src + suffix) for suffix in ('', '/', '/.', '/./', '//', '/.//.')]
        srcs += [
            (self.parent + '/./conf.d', self.parent + '/./conf.d'),
            (self.tmpdir + '/./etc/./conf.d/', self.tmpdir + '/./etc/./conf.d/'),
            (self.parent + '//conf.d/', self.src + '/'),
            (self.src + '/../conf.d/', self.src + '/../conf.d/'),
            (self.src + '/sub/deep/../../../conf.d', self.src + '/sub/deep/../../../conf.d'),
            (self.tmpdir + '/link/../etc/conf.d', self.tmpdir + '/link/../etc/conf.d'),
            ('/..' + self.src, self.src),
            ('/../..' + self.src + '/', self.src + '/'),
        ]
        for src, mapped_src in srcs:
            x = DecryptTester(self.loader)
            result = x.run(self._args(src=src, decrypt=True))
            self.assertFalse(result.get('failed'), (src, result.get('msg')))
            self._assert_staged_src(x, mapped_src)
            self._assert_staged_tree(x.staged)
            self._assert_clean()

    def test_decrypt_only_creates_directories_in_the_staging_dir(self):
        self._encrypt()
        before = self._outside_local_tmp()
        created = []
        real_mkdir = os.mkdir

        def mkdir(path, *args, **kwargs):
            created.append(os.path.join(os.path.realpath(os.path.dirname(path)), os.path.basename(path)))
            return real_mkdir(path, *args, **kwargs)

        for src in ('/..' + self.src, '/../..' + self.src + '/', self.src + '/sub/../sub/', self.tmpdir + '/./etc/conf.d'):
            x = DecryptTester(self.loader)
            with patch.object(os, 'mkdir', side_effect=mkdir):
                result = x.run(self._args(src=src, decrypt=True))
            self.assertFalse(result.get('failed'), (src, result.get('msg')))
            self.assertEqual(created[0], x.staging_dir)
            for path in created[1:]:
                self.assertTrue(path.startswith(x.staging_dir + '/'), path)
            del created[:]
            self._assert_clean()
        self.assertEqual(self._outside_local_tmp(), before)

    def test_decrypt_parent_directories(self):
        self._encrypt()
        self._write('../.rsync-filter', b'- plain.txt\n', 0o644, 1500000004)
        parents = []
        parent = self.parent
        while parent != '/':
            parents.append(parent)
            parent = os.path.dirname(parent)

        for src in (self.src, self.parent + '/./conf.d/', os.path.join(self.src, 'secret.yml')):
            x = DecryptTester(self.loader)
            result = x.run(self._args(src=src, decrypt=True))
            self.assertFalse(result.get('failed'))
            if src.endswith('secret.yml'):
                self.assertEqual(sorted(x.staged_parents), sorted(parents + ['/', self.src]))
            else:
                self.assertEqual(sorted(x.staged_parents), sorted(parents + ['/']))
            for parent in parents:
                self.assertEqual(x.staged_parents[parent].mode, os.stat(parent).st_mode, parent)
                self.assertNotEqual(x.staged_parents[parent].ino, os.stat(parent).st_ino, parent)
            for parent in (self.parent, self.tmpdir):
                self.assertEqual(x.staged_parents[parent].mtime, os.stat(parent).st_mtime_ns, parent)
            self.assertEqual(stat.S_IMODE(x.staged_parents[self.parent].mode), 0o751)
            self.assertEqual(x.staged_parents[self.parent].mtime, 1500000015 * 10 ** 9)
            self.assertEqual(stat.S_IMODE(x.staged_parents['/'].mode), 0o700)
            for parent in parents + ['/']:
                self.assertEqual(len(x.staged_parent_names[parent]), 1, parent)
            self._assert_clean()

    def test_decrypt_single_encrypted_file(self):
        self._encrypt()
        secret = os.path.join(self.src, 'secret.yml')
        before = self._outside_local_tmp()
        for src in (secret, self.src + '/./secret.yml', self.src + '/sub/../secret.yml'):
            x = DecryptTester(self.loader)
            result = x.run(self._args(src=src, decrypt=True))
            self.assertFalse(result.get('failed'))
            self._assert_staged_src(x, src)
            self.assertEqual(list(x.staged), ['secret.yml'])
            self.assertEqual(x.staged['secret.yml'].data, b'top secret\n')
            self.assertEqual(x.staged['secret.yml'].mode, os.stat(secret).st_mode)
            self.assertEqual(x.staged['secret.yml'].mtime, os.stat(secret).st_mtime_ns)
            self.assertNotEqual(x.staged['secret.yml'].ino, os.stat(secret).st_ino)
            self._assert_clean()
        self.assertEqual(self._outside_local_tmp(), before)

    def test_decrypt_single_plain_file(self):
        self._encrypt()
        plain = os.path.join(self.src, 'plain.txt')
        x = DecryptTester(self.loader)
        result = x.run(self._args(src=plain, decrypt=True))
        self.assertFalse(result.get('failed'))
        self.assertEqual(x.final_module_args['src'], plain)
        self.assertEqual(self._decrypted_paths(), [])
        self._assert_clean()

    def test_decrypt_leaves_the_source_untouched(self):
        self._encrypt()
        outside = os.path.join(self.tmpdir, 'outside')
        os.mkdir(outside)
        with open(os.path.join(outside, 'plain.txt'), 'wb') as f:
            f.write(b'outside\n')
        self._write('sub/deep/read_only.txt', b'read only\n', 0o400, 1500000003)
        self._symlink(outside, 'absolute_dir')
        self._symlink('../../outside', 'relative_dir')
        self._symlink('sub/deep', 'inside_dir')
        self._symlink('plain.txt', 'inside_file')
        for path in (outside, os.path.join(self.src, 'sub', 'deep'), os.path.join(self.src, 'sub'), os.path.join(self.src, 'empty'), self.src, self.parent):
            os.chmod(path, 0o555)
            self.addCleanup(os.chmod, path, 0o755)
        before = self._outside_local_tmp()

        def assert_unchanged_except_link_count():
            during = self._outside_local_tmp()
            self.assertEqual(sorted(during), sorted(before))
            for key in before:
                self.assertEqual(during[key][:5], before[key][:5], key)

        for link_error in (None, OSError(errno.EXDEV, os.strerror(errno.EXDEV))):
            for execute_side_effect in (None, BreakPoint()):
                x = DecryptTester(self.loader, execute_side_effect=execute_side_effect)
                execute_module = x._execute_module

                def execute(module_name, module_args=None, task_vars=None):
                    assert_unchanged_except_link_count()
                    return execute_module(module_name, module_args, task_vars)

                x._execute_module = execute
                with patch.object(os, 'link', wraps=os.link) as link:
                    link.side_effect = link_error
                    if execute_side_effect is None:
                        result = x.run(self._args(decrypt=True))
                        self.assertFalse(result.get('failed'), result.get('msg'))
                    else:
                        self.assertRaises(BreakPoint, x.run, self._args(decrypt=True))
                self.assertTrue(x.execute_called)
                self.assertEqual(stat.S_IMODE(x.staged['conf.d/sub/deep'].mode), 0o555)
                self.assertEqual(x.staged['conf.d/sub/deep/key.pem'].data, b'deep secret\n')
                self.assertEqual(x.staged['conf.d/sub/deep/read_only.txt'].nlink, 2 if link_error is None else 1)
                self._assert_clean()
                self.assertEqual(self._outside_local_tmp(), before)

    def test_decrypt_cleanup_only_changes_modes_in_the_staging_dir(self):
        self._encrypt()
        outside = os.path.join(self.tmpdir, 'outside')
        os.makedirs(os.path.join(outside, 'dir'))
        self._symlink(outside, 'absolute_dir')
        self._symlink('../../outside', 'relative_dir')
        for path in (os.path.join(outside, 'dir'), outside, os.path.join(self.src, 'sub', 'deep'), os.path.join(self.src, 'sub')):
            os.chmod(path, 0o500)
            self.addCleanup(os.chmod, path, 0o755)
        before = self._outside_local_tmp()

        changed = []
        real_chmod = os.chmod

        def chmod(path, *args, **kwargs):
            changed.append(path)
            self.assertFalse(os.path.islink(path), path)
            return real_chmod(path, *args, **kwargs)

        x = DecryptTester(self.loader)
        execute_module = x._execute_module

        def execute(module_name, module_args=None, task_vars=None):
            result = execute_module(module_name, module_args, task_vars)
            patcher = patch.object(os, 'chmod', side_effect=chmod)
            patcher.start()
            self.addCleanup(patcher.stop)
            return result

        x._execute_module = execute
        result = x.run(self._args(decrypt=True))
        self.assertFalse(result.get('failed'), result.get('msg'))
        self.assertIn(os.path.join(x.staging_dir + self.src, 'sub', 'deep'), [os.path.normpath(path) for path in changed])
        for path in changed:
            self.assertTrue(os.path.normpath(path).startswith(x.staging_dir + '/'), path)
        self._assert_clean()
        self.assertEqual(self._outside_local_tmp(), before)

    def test_decrypt_hard_link_fallback(self):
        self._encrypt()
        before = self._outside_local_tmp()
        plain = ('plain.txt', 'plain_only/plain.txt', 'sub/plain.txt')
        for code in (errno.EXDEV, errno.EPERM, errno.EACCES, errno.EMLINK):
            x = DecryptTester(self.loader)
            with patch.object(os, 'link', side_effect=OSError(code, os.strerror(code))) as link:
                result = x.run(self._args(decrypt=True))
            self.assertFalse(result.get('failed'), result.get('msg'))
            self.assertEqual(link.call_count, 3)
            self._assert_staged_tree(x.staged, copied=plain)
            for name in plain:
                self.assertEqual(x.staged['conf.d/' + name].nlink, 1)
            self._assert_clean()
            self.assertEqual(self._outside_local_tmp(), before)

    def test_decrypt_hard_link_fallback_for_some_files(self):
        self._encrypt()
        real_link = os.link

        def link(src, dst, *args, **kwargs):
            if src.endswith('/sub/plain.txt'):
                raise OSError(errno.EPERM, os.strerror(errno.EPERM))
            return real_link(src, dst, *args, **kwargs)

        x = DecryptTester(self.loader)
        with patch.object(os, 'link', side_effect=link):
            result = x.run(self._args(decrypt=True))
        self.assertFalse(result.get('failed'), result.get('msg'))
        self._assert_staged_tree(x.staged, copied=('sub/plain.txt',))
        self._assert_clean()

    def test_decrypt_copy_never_writes_to_an_existing_file(self):
        self._encrypt()
        plain = os.path.join(self.src, 'plain.txt')
        other = os.path.join(self.src, 'sub', 'plain.txt')
        before = snapshot(plain)
        x = DecryptTester(self.loader)
        SAM = ActionModule(x.task, x.connection, x._play_context, self.loader, x.templar, x.shared_loader_obj)
        staged = os.path.join(self.local_tmp, 'plain.txt')
        os.link(plain, staged)
        self.assertRaises(OSError, SAM._copy_file, other, staged, other)
        with patch.object(os, 'link', side_effect=OSError(errno.EEXIST, os.strerror(errno.EEXIST))):
            self.assertRaises(OSError, SAM._stage_file, other, staged)
        os.unlink(staged)
        self.assertEqual(snapshot(plain), before)

    def test_decrypt_special_file_that_cannot_be_hard_linked(self):
        self._encrypt()
        fifo = os.path.join(self.src, 'sub', 'fifo')
        os.mkfifo(fifo)
        x = DecryptTester(self.loader)
        with patch.object(os, 'link', side_effect=OSError(errno.EXDEV, os.strerror(errno.EXDEV))):
            result = x.run(self._args(decrypt=True))
        self.assertTrue(result.get('failed'))
        self.assertIn('Failed to decrypt %s' % fifo, result['msg'])
        self.assertIn('special file', result['msg'])
        self.assertFalse(x.execute_called)
        self._assert_clean()

    def test_decrypt_symlinks(self):
        self._encrypt()
        outside = os.path.join(self.tmpdir, 'outside')
        os.mkdir(outside)
        with open(os.path.join(outside, 'secret.yml'), 'wb') as f:
            f.write(self.top_secret)
        os.symlink(self.src, os.path.join(self.tmpdir, 'alias'))
        links = {
            'inside': ('secret.yml', b'top secret\n'),
            'sub/inside_up': ('../secret.yml', b'top secret\n'),
            'sub/inside_round': ('../../conf.d/sub/deep/key.pem', b'deep secret\n'),
            'inside_dir': ('sub/deep', None),
            'absolute': (os.path.join(outside, 'secret.yml'), self.top_secret),
            'absolute_inside': (os.path.join(self.src, 'secret.yml'), self.top_secret),
            'absolute_dir': (outside, None),
            'outside': ('../../outside/secret.yml', None),
            'sub/outside_dir': ('../../../outside', None),
            'reenter': ('../../alias/secret.yml', None),
            'dangling': ('missing', None),
            'root': ('../' * self.src.count('/') + 'dev/null', None),
        }
        for number, name in enumerate(sorted(links)):
            self._symlink(links[name][0], name, 1400000010 + number)
            self.assertEqual(os.path.exists(os.path.join(self.src, name)), name != 'dangling', name)
        before = self._outside_local_tmp()

        x = DecryptTester(self.loader)
        found = {}
        execute_module = x._execute_module

        def execute(module_name, module_args=None, task_vars=None):
            for name in links:
                found[name] = os.path.realpath(os.path.join(module_args['src'], name))
            return execute_module(module_name, module_args, task_vars)

        x._execute_module = execute
        result = x.run(self._args(decrypt=True))
        self.assertFalse(result.get('failed'), result.get('msg'))
        self._assert_staged_tree(x.staged)
        for name in links:
            self.assertEqual(x.staged['conf.d/' + name].data, links[name][0], name)
            self.assertEqual(x.staged['conf.d/' + name].target_data, links[name][1], name)
            self.assertEqual(x.staged['conf.d/' + name].mtime, os.lstat(os.path.join(self.src, name)).st_mtime_ns, name)
        staged_src = x.staging_dir + self.src
        self.assertEqual(found['inside_dir'], os.path.join(staged_src, 'sub', 'deep'))
        self.assertEqual(found['absolute_dir'], outside)
        self.assertEqual(found['outside'], os.path.join(x.staging_dir + self.tmpdir, 'outside', 'secret.yml'))
        self.assertEqual(found['sub/outside_dir'], os.path.join(x.staging_dir + self.tmpdir, 'outside'))
        self.assertEqual(found['reenter'], os.path.join(x.staging_dir + self.tmpdir, 'alias', 'secret.yml'))
        self.assertEqual(found['root'], os.path.join(x.staging_dir, 'dev', 'null'))
        self.assertEqual(x.staged_parent_names[self.tmpdir], ['etc'])
        self.assertEqual(x.staged_parent_names[self.parent], ['conf.d'])
        self.assertEqual(sorted(self._decrypted_paths()),
                         [os.path.join(self.src, 'secret.yml'), os.path.join(self.src, 'sub', 'deep', 'key.pem')])
        self._assert_clean()
        self.assertEqual(self._outside_local_tmp(), before)

    def test_decrypt_symlinks_that_point_above_the_root_directory(self):
        self._encrypt()
        with open(os.path.join(self.tmpdir, 'marker'), 'wb') as f:
            f.write(b'marker\n')
        depth = self.src.count('/')
        marker = self.tmpdir[1:] + '/marker'
        accepted = (
            ('exact', '../' * depth + marker),
            ('sub/exact', '../' * (depth + 1) + marker),
            ('consumed', 'sub/../' + '../' * depth + marker),
            ('sub/consumed', 'deep/./../' + '../' * (depth + 1) + marker),
            ('deeper', 'sub/deep/' + '../' * (depth + 2) + marker),
        )
        refused = (
            ('above', '../' * (depth + 1) + marker),
            ('far_above', '../' * (depth + 9) + 'ansiballz_cache'),
            ('sub/above', '../' * (depth + 2) + marker),
            ('consumed_above', 'sub/../' + '../' * (depth + 1) + marker),
            ('mixed_above', 'sub/deep/../../../' + '../' * depth + marker),
            ('deeper_above', 'sub/deep/' + '../' * (depth + 3) + marker),
            ('back_above', '../' * (depth + 1) + marker + '/../marker'),
            ('sub/deep/above_dir', '../' * (depth + 3)),
        )

        for name, target in accepted:
            path = self._symlink(target, name)
            with open(path, 'rb') as f:
                self.assertEqual(f.read(), b'marker\n', name)
        x = DecryptTester(self.loader)
        result = x.run(self._args(decrypt=True))
        self.assertFalse(result.get('failed'), result.get('msg'))
        self._assert_staged_tree(x.staged)
        for name, target in accepted:
            self.assertEqual(x.staged['conf.d/' + name].data, target, name)
            self.assertIsNone(x.staged['conf.d/' + name].target_data, name)
        self._assert_clean()

        for name, target in refused:
            path = self._symlink(target, name)
            before = self._outside_local_tmp()
            for src in (self.src, self.src + '/'):
                x = DecryptTester(self.loader)
                result = x.run(self._args(src=src, decrypt=True))
                self.assertTrue(result.get('failed'), name)
                self.assertIn('Failed to decrypt %s: the symbolic link points above the root directory' % path, result['msg'])
                self.assertFalse(x.execute_called)
                self._assert_clean()
            self.assertEqual(self._outside_local_tmp(), before)
            x = DecryptTester(self.loader)
            result = x.run(self._args())
            self.assertFalse(result.get('failed'))
            os.unlink(path)

    def test_decrypt_symlinks_that_point_outside_of_the_mirror(self):
        self._encrypt()
        with open(os.path.join(self.tmpdir, 'marker'), 'wb') as f:
            f.write(b'marker\n')
        os.symlink(self.src, os.path.join(self.tmpdir, 'alias'))
        self._symlink('/', 'sub/absolute_root')
        depth = self.src.count('/')
        links = (
            ('shallow', '../' * depth + self.tmpdir[1:] + '/marker'),
            ('sub/through_absolute', 'absolute_root/../' + self.tmpdir[1:] + '/marker'),
        )
        for name, target in links:
            path = self._symlink(target, name)
            with open(path, 'rb') as f:
                self.assertEqual(f.read(), b'marker\n', name)
            before = self._outside_local_tmp()
            src = os.path.join(self.tmpdir, 'alias') + '/'
            x = DecryptTester(self.loader)
            result = x.run(self._args(src=src, decrypt=True))
            self.assertTrue(result.get('failed'), name)
            self.assertIn('Failed to decrypt %s: the symbolic link points outside of the mirror' % os.path.join(self.tmpdir, 'alias', name), result['msg'])
            self.assertFalse(x.execute_called)
            self._assert_clean()
            self.assertEqual(self._outside_local_tmp(), before)
            os.unlink(path)

        self._symlink(links[0][1], links[0][0])
        x = DecryptTester(self.loader)
        result = x.run(self._args(decrypt=True))
        self.assertFalse(result.get('failed'), result.get('msg'))
        self.assertIsNone(x.staged['conf.d/shallow'].target_data)
        self._assert_clean()

    def test_decrypt_does_not_follow_symlinks(self):
        outside = os.path.join(self.tmpdir, 'outside')
        os.mkdir(outside)
        with open(os.path.join(outside, 'secret.yml'), 'wb') as f:
            f.write(self.top_secret)
        os.symlink(os.path.join(outside, 'secret.yml'), os.path.join(self.src, 'link.yml'))
        os.symlink(outside, os.path.join(self.src, 'linkdir'))

        for src in (self.src, self.src + '/'):
            x = DecryptTester(self.loader)
            result = x.run(self._args(src=src, decrypt=True))
            self.assertFalse(result.get('failed'))
            self.assertEqual(x.final_module_args['src'], src)
            self.assertEqual(self._decrypted_paths(), [])
            self._assert_clean()

    def test_decrypt_refuses_symlink_src(self):
        self._encrypt()
        os.symlink(self.src, os.path.join(self.tmpdir, 'alias'))
        os.symlink('etc/conf.d', os.path.join(self.tmpdir, 'relative_alias'))
        self._symlink('secret.yml', 'link.yml')
        self._symlink('missing', 'dangling')
        srcs = [os.path.join(self.tmpdir, 'alias'), os.path.join(self.tmpdir, 'relative_alias'),
                os.path.join(self.src, 'link.yml'), os.path.join(self.src, 'dangling'), os.path.join(self.tmpdir, 'alias', 'sub', '..', 'link.yml')]
        for src in srcs:
            for kwargs in ({}, {'copy_links': True}, {'rsync_opts': ['-L']}):
                x = DecryptTester(self.loader)
                self._assert_refused(x, x.run(self._args(src=src, decrypt=True, **kwargs)), 'symbolic link')
            x = DecryptTester(self.loader)
            result = x.run(self._args(src=src))
            self.assertFalse(result.get('failed'))
            self.assertEqual(x.final_module_args['src'], src)

    def test_decrypt_refuses_src_that_contains_the_local_tmp(self):
        self._encrypt()
        os.symlink(self.tmpdir, os.path.join(self.src, 'sub', 'up'))
        inner_tmp = os.path.join(self.src, 'sub', '.tmp')
        os.mkdir(inner_tmp)
        os.symlink(inner_tmp, os.path.join(self.tmpdir, 'tmplink'))
        cases = (
            (self.local_tmp, self.tmpdir),
            (self.local_tmp, self.tmpdir + '/'),
            (self.local_tmp, self.local_tmp + '/.'),
            (self.local_tmp, os.path.join(self.src, 'sub', 'up') + '/'),
            (inner_tmp, self.src),
            (inner_tmp, self.src + '/sub/'),
            (os.path.join(self.tmpdir, 'tmplink'), self.src + '/'),
        )
        for local_tmp, src in cases:
            x = DecryptTester(self.loader)
            with patch.object(C, 'DEFAULT_LOCAL_TMP', local_tmp), patch.object(tempfile, 'mkdtemp', side_effect=AssertionError('staging')):
                result = x.run(self._args(src=src, decrypt=True))
            self._assert_refused(x, result, 'local temporary directory')
            self.assertEqual(os.listdir(inner_tmp), [])

        x = DecryptTester(self.loader)
        with patch.object(C, 'DEFAULT_LOCAL_TMP', inner_tmp):
            result = x.run(self._args(src=self.src + '/plain_only/', decrypt=True))
        self.assertFalse(result.get('failed'))

    def test_decrypt_preserves_group_when_owner_cannot_be_set(self):
        self._encrypt()
        self._symlink('secret.yml', 'link')
        groups = {}

        def lchown(path, uid, gid):
            if uid != -1:
                raise OSError(errno.EPERM, os.strerror(errno.EPERM))
            groups[os.path.normpath(path)] = gid

        x = DecryptTester(self.loader)
        with patch.object(os, 'lchown', side_effect=lchown), patch.object(os, 'link', side_effect=OSError(errno.EXDEV, os.strerror(errno.EXDEV))):
            result = x.run(self._args(decrypt=True))
        self.assertFalse(result.get('failed'), result.get('msg'))
        staged_src = x.staging_dir + self.src
        for name in ('secret.yml', 'sub/deep/key.pem', 'plain.txt', 'link', 'sub', ''):
            self.assertEqual(groups[os.path.normpath(os.path.join(staged_src, name))], os.lstat(os.path.join(self.src, name)).st_gid, name)
        self.assertEqual(groups[x.staging_dir + self.parent], os.stat(self.parent).st_gid)
        self._assert_clean()

    @unittest.skipIf(os.geteuid() == 0, 'root can read every directory')
    def test_decrypt_unreadable_directory(self):
        self._encrypt()
        unreadable = os.path.join(self.src, 'plain_only')
        os.chmod(unreadable, 0o000)
        self.addCleanup(os.chmod, unreadable, 0o700)
        for src in (self.src, self.src + '/', unreadable + '/'):
            x = DecryptTester(self.loader)
            result = x.run(self._args(src=src, decrypt=True))
            self.assertTrue(result.get('failed'))
            self.assertIn('Failed to decrypt %s: the directory cannot be read' % unreadable, result['msg'])
            self.assertFalse(x.execute_called)
            self._assert_clean()

        x = DecryptTester(self.loader)
        SAM = ActionModule(x.task, x.connection, x._play_context, self.loader, x.templar, x.shared_loader_obj)
        staging_dir = tempfile.mkdtemp(dir=self.local_tmp)
        encrypted = set([os.path.join(self.src, 'secret.yml')])
        try:
            self.assertRaises(AnsibleError, SAM._stage_src, self.src, staging_dir, encrypted)
        finally:
            SAM._remove_staging_dir(staging_dir)
        self._assert_clean()

    def test_decrypt_symlinked_directory_content(self):
        self._encrypt()
        os.symlink(self.src, os.path.join(self.tmpdir, 'srclink'))
        for suffix in ('/', '/.'):
            src = os.path.join(self.tmpdir, 'srclink') + suffix
            x = DecryptTester(self.loader)
            result = x.run(self._args(src=src, decrypt=True))
            self.assertFalse(result.get('failed'))
            self._assert_staged_src(x, src)
            self._assert_staged_tree(x.staged, name='srclink')
            self._assert_clean()

    def test_decrypt_staging_modes(self):
        self._encrypt()
        self.addCleanup(os.umask, os.umask(0))
        x = DecryptTester(self.loader)
        modes = []
        real_mkdir, real_open = os.mkdir, os.open

        def mkdir(path, mode=0o777, **kwargs):
            modes.append(mode)
            return real_mkdir(path, mode, **kwargs)

        def os_open(path, flags, mode=0o777, **kwargs):
            if flags & os.O_CREAT:
                modes.append(mode)
                self.assertTrue(flags & os.O_EXCL, path)
            return real_open(path, flags, mode, **kwargs)

        with patch.object(os, 'mkdir', side_effect=mkdir), patch.object(os, 'open', side_effect=os_open):
            result = x.run(self._args(decrypt=True))
        self.assertFalse(result.get('failed'))
        self.assertEqual(x.staging_dir_mode, 0o700)
        self.assertEqual(sorted(set(modes)), [0o600, 0o700])
        self._assert_staged_tree(x.staged)
        self._assert_clean()

    def test_decrypt_tolerates_chown_failure(self):
        self._encrypt()
        self._symlink('secret.yml', 'link')
        x = DecryptTester(self.loader)
        with patch.object(os, 'lchown', side_effect=OSError(1, 'Operation not permitted')) as lchown:
            result = x.run(self._args(decrypt=True))
        self.assertTrue(lchown.called)
        self.assertFalse(result.get('failed'))
        self._assert_staged_tree(x.staged)
        self._assert_clean()

    def test_decrypt_only_changes_attributes_of_what_it_created(self):
        self._encrypt()
        self._symlink('secret.yml', 'link')
        self._symlink('sub', 'linkdir')
        self._symlink(self.parent, 'absolute_dir')
        created = set()
        changed = []
        real_mkdir, real_open, real_symlink = os.mkdir, os.open, os.symlink

        def mkdir(path, *args, **kwargs):
            real_mkdir(path, *args, **kwargs)
            created.add(os.lstat(path).st_ino)

        def os_open(path, flags, *args, **kwargs):
            fd = real_open(path, flags, *args, **kwargs)
            if flags & os.O_EXCL:
                created.add(os.fstat(fd).st_ino)
            return fd

        def symlink(src, dst, *args, **kwargs):
            real_symlink(src, dst, *args, **kwargs)
            created.add(os.lstat(dst).st_ino)

        def record(follow_symlinks):
            def change(path, *args, **kwargs):
                if follow_symlinks and kwargs.get('follow_symlinks', True):
                    changed.append((path, os.stat(path).st_ino))
                else:
                    changed.append((path, os.lstat(path).st_ino))
            return change

        x = DecryptTester(self.loader)
        with patch.object(os, 'mkdir', side_effect=mkdir), patch.object(os, 'open', side_effect=os_open), \
                patch.object(os, 'symlink', side_effect=symlink), \
                patch.object(os, 'chown', side_effect=record(True)), patch.object(os, 'lchown', side_effect=record(False)) as lchown, \
                patch.object(os, 'chmod', side_effect=record(True)) as chmod, patch.object(os, 'utime', side_effect=record(True)) as utime:
            result = x.run(self._args(decrypt=True))
        self.assertFalse(result.get('failed'), result.get('msg'))
        for mock in (lchown, chmod, utime):
            self.assertTrue(mock.called)
        for path, ino in changed:
            self.assertIn(ino, created, path)
        self._assert_clean()

    def test_decrypt_removes_staging_dir_when_module_raises(self):
        self._encrypt()
        for side_effect in (BreakPoint(), KeyboardInterrupt()):
            x = DecryptTester(self.loader, execute_side_effect=side_effect)
            self.assertRaises(type(side_effect), x.run, self._args(decrypt=True))
            self.assertTrue(x.execute_called)
            self._assert_staged_tree(x.staged)
            self._assert_clean()

    def test_decrypt_removes_staging_dir_when_staging_raises(self):
        self._encrypt()
        before = self._outside_local_tmp()
        for name in ('copystat', 'copyfileobj'):
            for side_effect in (BreakPoint(), KeyboardInterrupt()):
                x = DecryptTester(self.loader)
                with patch.object(shutil, name, side_effect=side_effect):
                    self.assertRaises(type(side_effect), x.run, self._args(decrypt=True))
                self.assertFalse(x.execute_called)
                self._assert_clean()
        self.assertEqual(self._outside_local_tmp(), before)

    def test_decrypt_staging_os_error(self):
        self._encrypt()
        for name in ('copystat', 'copyfileobj'):
            x = DecryptTester(self.loader)
            with patch.object(shutil, name, side_effect=OSError(13, 'Permission denied')):
                result = x.run(self._args(decrypt=True))
            self.assertTrue(result.get('failed'))
            self.assertIn('Failed to decrypt %s: ' % self.src, result['msg'])
            self.assertFalse(x.execute_called)
            self._assert_clean()

    def test_decrypt_file_names_with_special_characters(self):
        self._encrypt()
        for name in ('a$HOME.txt', '${HOME}', "'quoted'", '"double"', '~user', 'sp ace.txt'):
            self._write(name, b'plain\n', 0o644, 1500000005)
        self._write('$SYNCHRONIZE_UNDEFINED.yml', self.top_secret, 0o600, 1400000002)

        x = DecryptTester(self.loader)
        result = x.run(self._args(decrypt=True))
        self.assertFalse(result.get('failed'), result.get('msg'))
        self._assert_staged_tree(x.staged, decrypted={
            'secret.yml': b'top secret\n', 'sub/deep/key.pem': b'deep secret\n', '$SYNCHRONIZE_UNDEFINED.yml': b'top secret\n'})
        self._assert_clean()

        src = os.path.join(self.src, '$SYNCHRONIZE_UNDEFINED.yml')
        x = DecryptTester(self.loader)
        result = x.run(self._args(src=src, decrypt=True))
        self.assertFalse(result.get('failed'), result.get('msg'))
        self._assert_staged_src(x, src)
        self.assertEqual(x.staged['$SYNCHRONIZE_UNDEFINED.yml'].data, b'top secret\n')
        self._assert_clean()

    def test_decrypt_encrypted_file_name_with_variable_fails_cleanly(self):
        self._write('a$HOME.yml', self.top_secret, 0o600, 1400000002)
        x = DecryptTester(self.loader)
        result = x.run(self._args(decrypt=True))
        self.assertTrue(result.get('failed'))
        self.assertIn('Failed to decrypt %s' % os.path.join(self.src, 'a$HOME.yml'), result['msg'])
        self.assertFalse(x.execute_called)
        self.assertEqual(self._decrypted_paths(), [])
        self._assert_clean()

    def test_decrypt_encrypted_file_name_does_not_substitute_another_file(self):
        for other in (b'OTHER PLAIN\n', self.deep_secret):
            self._write('$SYNCHRONIZE_X.yml', self.top_secret, 0o600, 1400000002)
            self._write('other.yml', other, 0o644, 1400000003)
            self.loader.get_real_file.reset_mock()
            x = DecryptTester(self.loader)
            with patch.dict(os.environ, {'SYNCHRONIZE_X': 'other'}):
                result = x.run(self._args(decrypt=True))
            self.assertTrue(result.get('failed'))
            self.assertIn('Failed to decrypt %s' % os.path.join(self.src, '$SYNCHRONIZE_X.yml'), result['msg'])
            self.assertFalse(x.execute_called)
            self.assertNotIn(os.path.join(self.src, '$SYNCHRONIZE_X.yml'), self._decrypted_paths())
            self._assert_clean()

    def test_decrypt_refuses_src_with_environment_variable(self):
        self._encrypt()
        os.mkdir(os.path.join(self.tmpdir, '$SYNCHRONIZE_X'))
        with patch.dict(os.environ, {'SYNCHRONIZE_X': 'etc'}):
            for src in (os.path.join(self.tmpdir, '$SYNCHRONIZE_X', 'conf.d'), os.path.join(self.tmpdir, '${SYNCHRONIZE_X}', 'conf.d') + '/'):
                x = DecryptTester(self.loader)
                self._assert_refused(x, x.run(self._args(src=src, decrypt=True)), 'environment variable')
                x = DecryptTester(self.loader)
                result = x.run(self._args(src=src))
                self.assertFalse(result.get('failed'))
                self.assertEqual(x.final_module_args['src'], src)

    def test_decrypt_refuses_loader_result_outside_local_tmp(self):
        self._encrypt()
        other = self._write('other.yml', b'OTHER PLAIN\n', 0o644, 1400000003)
        outside = os.path.join(self.tmpdir, 'outside.yml')
        with open(outside, 'wb') as f:
            f.write(b'OUTSIDE\n')
        secret = os.path.join(self.src, 'secret.yml')
        for returned in (other, outside, secret):
            loader = MagicMock()
            loader.path_dwim.side_effect = lambda path: path
            loader.get_real_file.return_value = returned
            x = DecryptTester(loader)
            result = x.run(self._args(src=secret, decrypt=True))
            self.assertTrue(result.get('failed'))
            self.assertIn('Failed to decrypt %s' % secret, result['msg'])
            self.assertFalse(x.execute_called)
            self.assertFalse(loader.cleanup_tmp_file.called)
            self.assertTrue(os.path.exists(returned))
            self._assert_clean()

    def test_decrypt_removes_the_decrypted_file_of_the_loader(self):
        self._encrypt()
        self.loader.cleanup_tmp_file = MagicMock(wraps=self.loader.cleanup_tmp_file)
        x = DecryptTester(self.loader)
        result = x.run(self._args(decrypt=True))
        self.assertFalse(result.get('failed'))
        self.assertEqual(self.loader.cleanup_tmp_file.call_count, 2)
        for call in self.loader.cleanup_tmp_file.call_args_list:
            self.assertEqual(os.path.dirname(call[0][0]), self.local_tmp)
        self._assert_clean()

    @unittest.skipIf(os.geteuid() == 0, 'root can read every file')
    def test_decrypt_unreadable_file(self):
        self._encrypt()
        self._write('unreadable.txt', self.top_secret, 0o000, 1500000006)
        x = DecryptTester(self.loader)
        result = x.run(self._args(decrypt=True))
        self.assertFalse(result.get('failed'), result.get('msg'))
        self.assertTrue(x.execute_called)
        self._assert_staged_tree(x.staged)
        self._assert_clean()

        x = DecryptTester(self.loader)
        with patch.object(os, 'link', side_effect=OSError(errno.EXDEV, os.strerror(errno.EXDEV))):
            result = x.run(self._args(decrypt=True))
        self.assertTrue(result.get('failed'))
        self.assertIn('Failed to decrypt', result['msg'])
        self.assertIn('unreadable.txt', result['msg'])
        self.assertFalse(x.execute_called)
        self._assert_clean()

        unreadable = os.path.join(self.src, 'unreadable.txt')
        x = DecryptTester(self.loader)
        result = x.run(self._args(src=unreadable, decrypt=True))
        self.assertFalse(result.get('failed'), result.get('msg'))
        self.assertEqual(x.final_module_args['src'], unreadable)
        self._assert_clean()

    def test_decrypt_passes_rsync_options_through(self):
        self._encrypt()
        cases = [dict(rsync_opts=rsync_opts) for rsync_opts in (
            None, [], 42, '--no-motd', '--no-motd,--relative', '-R', ['--relative'], ['-avR'], ['--no-implied-dirs', '-R'],
            ['--files-from=x'], ['--files-from', '/tmp/list'], ['-L'], ['--copy-links'], ['--copy-unsafe-links'], ['-k'], ['--safe-links'],
            ['--compress --relative'], ["--exclude='unbalanced -R"], ['-e', 'ssh -R 8080:localhost:80'], ['--', '-R'], ['-H', '--anything'],
        )]
        cases += [dict(copy_links=True), dict(copy_links='yes', links=False), dict(link_dest=['/tmp/a --relative', '/tmp/b -L']),
                  dict(delete=True, recursive=True, checksum=True, archive=False)]
        for case in cases:
            expected = DecryptTester(None)
            expected.run(self._args(**case))
            x = DecryptTester(self.loader)
            result = x.run(self._args(decrypt=True, **case))
            self.assertFalse(result.get('failed'), case)
            self._assert_staged_src(x, self.src)
            self._assert_staged_tree(x.staged)
            self.assertIs(x.final_module_args.pop('decrypt'), True)
            x.final_module_args['src'] = self.src
            self.assertEqual(x.final_module_args, expected.final_module_args, case)
            self._assert_clean()

        for rsync_path in ('/usr/bin/rsync --relative', 'rsync -zL', "'/opt/my rsync/rsync' --files-from=/tmp/list"):
            x = DecryptTester(self.loader)
            result = x.run(self._args(decrypt=True), task_vars={'ansible_rsync_path': rsync_path})
            self.assertFalse(result.get('failed'), rsync_path)
            self.assertEqual(x.final_module_args['_local_rsync_path'], rsync_path)
            self._assert_staged_src(x, self.src)
            self._assert_clean()

    def test_decrypt_refuses_parent_directory_as_last_component(self):
        self._encrypt()
        for src in (self.src + '/..', self.src + '/../', self.src + '/sub/../.', self.src + '/sub/..//./'):
            x = DecryptTester(self.loader)
            self._assert_refused(x, x.run(self._args(src=src, decrypt=True)), "'..'")

    def test_decrypt_refuses_root_directory(self):
        for src in ('/', '//', '/.', '/./'):
            x = DecryptTester(self.loader)
            self._assert_refused(x, x.run(self._args(src=src, decrypt=True)), 'root directory')

    def test_decrypt_parent_directory_reference_behind_symlink(self):
        self._encrypt()
        real_parent = os.path.join(self.tmpdir, 'far', 'b')
        os.makedirs(os.path.join(self.tmpdir, 'far', 'deep'))
        os.mkdir(real_parent)
        shutil.move(self.src, os.path.join(real_parent, 'conf.d'))
        os.symlink(os.path.join(self.tmpdir, 'far', 'deep'), os.path.join(self.tmpdir, 'a'))
        os.makedirs(os.path.join(self.tmpdir, 'b', 'conf.d'))
        with open(os.path.join(self.tmpdir, 'b', 'conf.d', 'secret.yml'), 'wb') as f:
            f.write(self.other_secret)
        self.src = os.path.join(real_parent, 'conf.d')

        for suffix in ('', '/'):
            src = os.path.join(self.tmpdir, 'a', '..', 'b', 'conf.d') + suffix
            x = DecryptTester(self.loader)
            result = x.run(self._args(src=src, decrypt=True))
            self.assertFalse(result.get('failed'), result.get('msg'))
            self._assert_staged_src(x, src)
            self._assert_staged_tree(x.staged)
            self._assert_clean()

    def test_decrypt_refuses_mode_pull(self):
        x = DecryptTester(self.loader)
        self._assert_refused(x, x.run(self._args(decrypt=True, mode='pull')))

    def test_decrypt_refuses_remote_delegate(self):
        x = DecryptTester(self.loader)
        self._assert_refused(x, x.run(self._args(decrypt=True), delegate_to='u1404'))

    def test_decrypt_refuses_delegate_to_target(self):
        x = DecryptTester(self.loader)
        self._assert_refused(x, x.run(self._args(decrypt=True), delegate_to='el6host'))

    def test_decrypt_refuses_remote_src(self):
        for src in ('otherhost:/etc/conf.d', 'user@otherhost:/etc/conf.d', 'rsync://otherhost/module/conf.d'):
            x = DecryptTester(self.loader)
            self._assert_refused(x, x.run(self._args(src=src, decrypt=True)))

    def test_decrypt_local_connection(self):
        self._encrypt()
        for delegate_to in (None, 'localhost'):
            x = DecryptTester(self.loader)
            result = x.run(self._args(decrypt=True), transport='local', delegate_to=delegate_to)
            self.assertFalse(result.get('failed'))
            self._assert_staged_src(x, self.src)
            self._assert_staged_tree(x.staged)
            self._assert_clean()

    def test_decrypt_loader_error(self):
        self._encrypt()
        self._write('sub/broken.yml', self.other_secret, 0o600, 1400000002)
        x = DecryptTester(self.loader)
        result = x.run(self._args(decrypt=True))
        self.assertTrue(result.get('failed'))
        self.assertIn('Failed to decrypt %s: ' % os.path.join(self.src, 'sub', 'broken.yml'), result['msg'])
        self.assertFalse(x.execute_called)
        self._assert_clean()

    def test_decrypt_without_vault_secret(self):
        self._encrypt()
        x = DecryptTester(DataLoader())
        result = x.run(self._args(decrypt=True))
        self.assertTrue(result.get('failed'))
        self.assertIn('Failed to decrypt', result['msg'])
        self.assertFalse(x.execute_called)
        self._assert_clean()
