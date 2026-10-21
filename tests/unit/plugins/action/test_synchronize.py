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

    def __init__(self, loader, execute_side_effect=None, inspect=None):
        self.task = TaskMock()
        self.connection = ConnectionMock()
        self._play_context = PlayContextMock()
        self.loader = loader
        self.execute_side_effect = execute_side_effect
        self.inspect = inspect
        self.final_module_args = None
        self.staging_dir = None
        self.staging_dir_mode = None
        self.staged = None
        self.staged_parents = None
        self.staged_parent_names = None

    def _execute_module(self, module_name, module_args=None, task_vars=None):
        self.execute_called = True
        self.final_module_args = module_args
        if self.inspect is not None:
            self.inspect(module_args)
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

    def run(self, task_args, transport='ssh', delegate_to=None, task_vars=None):
        fixturepath = os.path.join(os.path.dirname(__file__), 'fixtures', 'synchronize', 'basic')
        with open(os.path.join(fixturepath, 'taskvars_in.json'), 'rb') as f:
            in_task_vars = json.loads(f.read().decode('utf-8'))
        for host in ('127.0.0.1', '::1', 'localhost'):
            in_task_vars['hostvars'][host] = {}
        in_task_vars.update(task_vars or {})

        self.task.args = task_args
        self.task.delegate_to = delegate_to
        self.connection.transport = transport

        SAM = ActionModule(self.task, self.connection, self._play_context,
                           self.loader, self.templar, self.shared_loader_obj)
        SAM._execute_module = self._execute_module
        return SAM.run(task_vars=in_task_vars)


Entry = namedtuple('Entry', ['data', 'target_data', 'mode', 'mtime', 'ino', 'nlink'])


def os_error(code):
    return OSError(code, os.strerror(code))


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

    def _create_outside(self, name, data):
        ''' Creates a directory next to the parent directory of self.src with one file in it '''
        outside = os.path.join(self.tmpdir, 'outside')
        os.mkdir(outside)
        with open(os.path.join(outside, name), 'wb') as f:
            f.write(data)
        return outside

    def _create_marker(self):
        with open(os.path.join(self.tmpdir, 'marker'), 'wb') as f:
            f.write(b'marker\n')
        return self.tmpdir[1:] + '/marker'

    def _args(self, **kwargs):
        args = {'src': self.src, 'dest': '/tmp/deleteme'}
        args.update(kwargs)
        return args

    def _run(self, loader=None, execute_side_effect=None, inspect=None, transport='ssh', delegate_to=None, task_vars=None, **kwargs):
        ''' Runs the action plugin with decrypt, returns the tester and the result '''
        x = DecryptTester(loader or self.loader, execute_side_effect=execute_side_effect, inspect=inspect)
        kwargs.setdefault('decrypt', True)
        return x, x.run(self._args(**kwargs), transport=transport, delegate_to=delegate_to, task_vars=task_vars)

    def _run_without_decrypt(self, **kwargs):
        x = DecryptTester(None)
        return x, x.run(self._args(**kwargs))

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

    def _assert_succeeded(self, x, result):
        self.assertFalse(result.get('failed'), result.get('msg'))
        self.assertTrue(x.execute_called)
        self._assert_clean()

    def _assert_failed(self, x, result, msg):
        self.assertTrue(result.get('failed'))
        self.assertIn(msg, result['msg'])
        self.assertFalse(x.execute_called)
        self._assert_clean()

    def _assert_refused(self, x, result, msg='decrypt'):
        self._assert_failed(x, result, msg)
        self.assertEqual(self._decrypted_paths(), [])

    def _assert_not_staged(self, x, result, src):
        self._assert_succeeded(x, result)
        self.assertEqual(x.final_module_args['src'], src)
        self.assertEqual(self._decrypted_paths(), [])

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

    def _assert_staged(self, x, result, src=None, **kwargs):
        self._assert_succeeded(x, result)
        self._assert_staged_src(x, src or self.src)
        self._assert_staged_tree(x.staged, **kwargs)

    def test_decrypt_unset_or_false_changes_nothing(self):
        self._encrypt()
        final_args = []
        for args in ({}, {'decrypt': False}, {'decrypt': 'no'}):
            with self.subTest(args=args):
                loader = MagicMock()
                x = DecryptTester(loader)
                with patch.object(tempfile, 'mkdtemp', side_effect=AssertionError('staging')):
                    result = x.run(self._args(**args))
                self._assert_succeeded(x, result)
                self.assertEqual(loader.mock_calls, [])
                x.final_module_args.pop('decrypt', None)
                final_args.append(x.final_module_args)
        self.assertEqual(final_args[0], final_args[1])
        self.assertEqual(final_args[0], final_args[2])
        self.assertEqual(final_args[0]['src'], self.src)

    def test_decrypt_unset_works_without_loader(self):
        x, result = self._run_without_decrypt()
        self._assert_succeeded(x, result)

    def test_decrypt_without_encrypted_files_does_not_stage(self):
        for src in (self.src, self.src + '/', os.path.join(self.src, 'plain.txt'), os.path.join(self.src, 'missing')):
            with self.subTest(src=src):
                expected, dummy = self._run_without_decrypt(src=src)
                with patch.object(tempfile, 'mkdtemp', side_effect=AssertionError('staging')), \
                        patch.object(os, 'link', side_effect=AssertionError('staging')):
                    x, result = self._run(src=src)
                self._assert_not_staged(x, result, src)
                self.assertIs(x.final_module_args.pop('decrypt'), True)
                self.assertEqual(x.final_module_args, expected.final_module_args)

    def test_decrypt_directory(self):
        self._encrypt()
        os.mkfifo(os.path.join(self.src, 'sub', 'fifo'))
        os.utime(os.path.join(self.src, 'sub'), (1500000011, 1500000011))
        before = self._outside_local_tmp()

        x, result = self._run()
        self._assert_staged(x, result)
        self.assertEqual(sorted(self._decrypted_paths()),
                         [os.path.join(self.src, 'secret.yml'), os.path.join(self.src, 'sub', 'deep', 'key.pem')])
        self.assertEqual(x.staged['conf.d/plain.txt'].data, b'plain\n')
        self.assertEqual(x.staged['conf.d/plain_only/plain.txt'].data, b'plain only\n')
        self.assertTrue(stat.S_ISDIR(x.staged['conf.d/empty'].mode))
        self.assertTrue(stat.S_ISFIFO(x.staged['conf.d/sub/fifo'].mode))
        self.assertEqual(stat.S_IMODE(x.staged['conf.d/secret.yml'].mode), 0o600)
        self.assertEqual(x.staged['conf.d/secret.yml'].mtime, 1400000000 * 10 ** 9)
        self.assertEqual(stat.S_IMODE(x.staged['conf.d/sub'].mode), 0o750)
        self.assertEqual(x.staged['conf.d/sub'].mtime, 1500000011 * 10 ** 9)
        self.assertEqual(self._outside_local_tmp(), before)

    def test_decrypt_source_path_mapping(self):
        self._encrypt()
        os.symlink(self.parent, os.path.join(self.tmpdir, 'link'))
        os.symlink(self.src, os.path.join(self.tmpdir, 'srclink'))
        cases = [(self.src + suffix, self.src + suffix, 'conf.d') for suffix in ('', '/', '/.', '/./', '//', '/.//.')]
        cases += [
            (self.parent + '/./conf.d', self.parent + '/./conf.d', 'conf.d'),
            (self.tmpdir + '/./etc/./conf.d/', self.tmpdir + '/./etc/./conf.d/', 'conf.d'),
            (self.parent + '//conf.d/', self.src + '/', 'conf.d'),
            (self.src + '/../conf.d/', self.src + '/../conf.d/', 'conf.d'),
            (self.src + '/sub/deep/../../../conf.d', self.src + '/sub/deep/../../../conf.d', 'conf.d'),
            (self.tmpdir + '/link/../etc/conf.d', self.tmpdir + '/link/../etc/conf.d', 'conf.d'),
            ('/..' + self.src, self.src, 'conf.d'),
            ('/../..' + self.src + '/', self.src + '/', 'conf.d'),
            (self.tmpdir + '/srclink/', self.tmpdir + '/srclink/', 'srclink'),
            (self.tmpdir + '/srclink/.', self.tmpdir + '/srclink/.', 'srclink'),
        ]
        for src, mapped_src, name in cases:
            with self.subTest(src=src):
                x, result = self._run(src=src)
                self._assert_staged(x, result, src=mapped_src, name=name)

    def test_decrypt_only_creates_directories_in_the_staging_dir(self):
        self._encrypt()
        before = self._outside_local_tmp()
        for src in ('/..' + self.src, '/../..' + self.src + '/', self.src + '/sub/../sub/', self.tmpdir + '/./etc/conf.d'):
            with self.subTest(src=src):
                with patch.object(os, 'mkdir', wraps=os.mkdir) as mkdir:
                    x, result = self._run(src=src)
                self._assert_succeeded(x, result)
                created = [os.path.normpath(call[0][0]) for call in mkdir.call_args_list]
                self.assertEqual(created[0], x.staging_dir)
                for path in created[1:]:
                    self.assertTrue(path.startswith(x.staging_dir + '/'), path)
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
            with self.subTest(src=src):
                x, result = self._run(src=src)
                self._assert_succeeded(x, result)
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
            with self.subTest(suffix=suffix):
                src = os.path.join(self.tmpdir, 'a', '..', 'b', 'conf.d') + suffix
                x, result = self._run(src=src)
                self._assert_staged(x, result, src=src)

    def test_decrypt_single_encrypted_file(self):
        self._encrypt()
        secret = os.path.join(self.src, 'secret.yml')
        before = self._outside_local_tmp()
        for src in (secret, self.src + '/./secret.yml', self.src + '/sub/../secret.yml'):
            with self.subTest(src=src):
                x, result = self._run(src=src)
                self._assert_succeeded(x, result)
                self._assert_staged_src(x, src)
                self.assertEqual(list(x.staged), ['secret.yml'])
                self.assertEqual(x.staged['secret.yml'].data, b'top secret\n')
                self.assertEqual(x.staged['secret.yml'].mode, os.stat(secret).st_mode)
                self.assertEqual(x.staged['secret.yml'].mtime, os.stat(secret).st_mtime_ns)
                self.assertNotEqual(x.staged['secret.yml'].ino, os.stat(secret).st_ino)
        self.assertEqual(self._outside_local_tmp(), before)

    def test_decrypt_single_plain_file(self):
        self._encrypt()
        plain = os.path.join(self.src, 'plain.txt')
        x, result = self._run(src=plain)
        self._assert_not_staged(x, result, plain)

    def test_decrypt_local_connection(self):
        self._encrypt()
        for delegate_to in (None, 'localhost'):
            with self.subTest(delegate_to=delegate_to):
                x, result = self._run(transport='local', delegate_to=delegate_to)
                self._assert_staged(x, result)

    def test_decrypt_leaves_the_source_untouched(self):
        self._encrypt()
        outside = self._create_outside('plain.txt', b'outside\n')
        self._write('sub/deep/read_only.txt', b'read only\n', 0o400, 1500000003)
        self._symlink(outside, 'absolute_dir')
        self._symlink('../../outside', 'relative_dir')
        self._symlink('sub/deep', 'inside_dir')
        self._symlink('plain.txt', 'inside_file')
        for path in (outside, os.path.join(self.src, 'sub', 'deep'), os.path.join(self.src, 'sub'), os.path.join(self.src, 'empty'), self.src, self.parent):
            os.chmod(path, 0o555)
            self.addCleanup(os.chmod, path, 0o755)
        before = self._outside_local_tmp()

        def assert_unchanged_except_link_count(module_args):
            during = self._outside_local_tmp()
            self.assertEqual(sorted(during), sorted(before))
            for key in before:
                self.assertEqual(during[key][:5], before[key][:5], key)

        for link_error in (None, os_error(errno.EXDEV)):
            for execute_side_effect in (None, BreakPoint()):
                with self.subTest(link_error=link_error, execute_side_effect=execute_side_effect):
                    with patch.object(os, 'link', wraps=os.link) as link:
                        link.side_effect = link_error
                        if execute_side_effect is None:
                            x, result = self._run(inspect=assert_unchanged_except_link_count)
                            self._assert_succeeded(x, result)
                        else:
                            x = DecryptTester(self.loader, execute_side_effect=execute_side_effect, inspect=assert_unchanged_except_link_count)
                            self.assertRaises(BreakPoint, x.run, self._args(decrypt=True))
                    self.assertTrue(x.execute_called)
                    self.assertEqual(stat.S_IMODE(x.staged['conf.d/sub/deep'].mode), 0o555)
                    self.assertEqual(x.staged['conf.d/sub/deep/key.pem'].data, b'deep secret\n')
                    self.assertEqual(x.staged['conf.d/sub/deep/read_only.txt'].nlink, 2 if link_error is None else 1)
                    self._assert_clean()
                    self.assertEqual(self._outside_local_tmp(), before)

    def test_decrypt_cleanup_only_changes_modes_in_the_staging_dir(self):
        self._encrypt()
        outside = self._create_outside('plain.txt', b'outside\n')
        os.mkdir(os.path.join(outside, 'dir'))
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

        def record_chmod(module_args):
            patcher = patch.object(os, 'chmod', side_effect=chmod)
            patcher.start()
            self.addCleanup(patcher.stop)

        x, result = self._run(inspect=record_chmod)
        self._assert_succeeded(x, result)
        self.assertIn(os.path.join(x.staging_dir + self.src, 'sub', 'deep'), [os.path.normpath(path) for path in changed])
        for path in changed:
            self.assertTrue(os.path.normpath(path).startswith(x.staging_dir + '/'), path)
        self.assertEqual(self._outside_local_tmp(), before)

    def test_decrypt_hard_link_fallback(self):
        self._encrypt()
        before = self._outside_local_tmp()
        plain = ('plain.txt', 'plain_only/plain.txt', 'sub/plain.txt')
        for code in (errno.EXDEV, errno.EPERM):
            with self.subTest(code=code):
                with patch.object(os, 'link', side_effect=os_error(code)) as link:
                    x, result = self._run()
                self._assert_staged(x, result, copied=plain)
                self.assertEqual(link.call_count, 3)
                for name in plain:
                    self.assertEqual(x.staged['conf.d/' + name].nlink, 1)
                self.assertEqual(self._outside_local_tmp(), before)

    def test_decrypt_hard_link_fallback_for_some_files(self):
        self._encrypt()
        real_link = os.link

        def link(src, dst, *args, **kwargs):
            if src.endswith('/sub/plain.txt'):
                raise os_error(errno.EPERM)
            return real_link(src, dst, *args, **kwargs)

        with patch.object(os, 'link', side_effect=link):
            x, result = self._run()
        self._assert_staged(x, result, copied=('sub/plain.txt',))

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
        with patch.object(os, 'link', side_effect=os_error(errno.EEXIST)):
            self.assertRaises(OSError, SAM._stage_file, other, staged)
        os.unlink(staged)
        self.assertEqual(snapshot(plain), before)

    def test_decrypt_special_file_that_cannot_be_hard_linked(self):
        self._encrypt()
        fifo = os.path.join(self.src, 'sub', 'fifo')
        os.mkfifo(fifo)
        with patch.object(os, 'link', side_effect=os_error(errno.EXDEV)):
            x, result = self._run()
        self._assert_failed(x, result, 'Failed to decrypt %s' % fifo)
        self.assertIn('special file', result['msg'])

    def test_decrypt_symlinks(self):
        self._encrypt()
        outside = self._create_outside('secret.yml', self.top_secret)
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
        found = {}

        def resolve(module_args):
            for name in links:
                found[name] = os.path.realpath(os.path.join(module_args['src'], name))

        x, result = self._run(inspect=resolve)
        self._assert_staged(x, result)
        for name in links:
            with self.subTest(name=name):
                self.assertEqual(x.staged['conf.d/' + name].data, links[name][0])
                self.assertEqual(x.staged['conf.d/' + name].target_data, links[name][1])
                self.assertEqual(x.staged['conf.d/' + name].mtime, os.lstat(os.path.join(self.src, name)).st_mtime_ns)
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
        self.assertEqual(self._outside_local_tmp(), before)

    def test_decrypt_symlinks_that_point_above_the_root_directory(self):
        self._encrypt()
        marker = self._create_marker()
        depth = self.src.count('/')
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
        x, result = self._run()
        self._assert_staged(x, result)
        for name, target in accepted:
            with self.subTest(name=name):
                self.assertEqual(x.staged['conf.d/' + name].data, target)
                self.assertIsNone(x.staged['conf.d/' + name].target_data)

        for name, target in refused:
            path = self._symlink(target, name)
            before = self._outside_local_tmp()
            for src in (self.src, self.src + '/'):
                with self.subTest(name=name, src=src):
                    x, result = self._run(src=src)
                    self._assert_failed(x, result, 'Failed to decrypt %s: the symbolic link points above the root directory' % path)
            with self.subTest(name=name, decrypt=False):
                self.assertEqual(self._outside_local_tmp(), before)
                x, result = self._run_without_decrypt()
                self._assert_succeeded(x, result)
            os.unlink(path)

    def test_decrypt_symlinks_that_point_outside_of_the_mirror(self):
        self._encrypt()
        marker = self._create_marker()
        os.symlink(self.src, os.path.join(self.tmpdir, 'alias'))
        self._symlink('/', 'sub/absolute_root')
        links = (
            ('shallow', '../' * self.src.count('/') + marker),
            ('sub/through_absolute', 'absolute_root/../' + marker),
        )
        src = os.path.join(self.tmpdir, 'alias') + '/'
        for name, target in links:
            with self.subTest(name=name):
                path = self._symlink(target, name)
                with open(path, 'rb') as f:
                    self.assertEqual(f.read(), b'marker\n')
                before = self._outside_local_tmp()
                x, result = self._run(src=src)
                link = os.path.join(self.tmpdir, 'alias', name)
                self._assert_failed(x, result, 'Failed to decrypt %s: the symbolic link points outside of the mirror' % link)
                self.assertEqual(self._outside_local_tmp(), before)
                os.unlink(path)

        self._symlink(links[0][1], links[0][0])
        x, result = self._run()
        self._assert_succeeded(x, result)
        self.assertIsNone(x.staged['conf.d/shallow'].target_data)

    def test_decrypt_does_not_follow_symlinks(self):
        outside = self._create_outside('secret.yml', self.top_secret)
        os.symlink(os.path.join(outside, 'secret.yml'), os.path.join(self.src, 'link.yml'))
        os.symlink(outside, os.path.join(self.src, 'linkdir'))

        for src in (self.src, self.src + '/'):
            with self.subTest(src=src):
                x, result = self._run(src=src)
                self._assert_not_staged(x, result, src)

    def test_decrypt_refuses_src(self):
        self._encrypt()
        controller = 'decrypt can only be used when the source is on the Ansible controller'
        cases = [
            ({'mode': 'pull'}, None, controller),
            ({}, 'u1404', controller),
            ({}, 'el6host', controller),
            ({'src': 'otherhost:/etc/conf.d'}, None, controller),
            ({'src': 'user@otherhost:/etc/conf.d'}, None, controller),
            ({'src': 'rsync://otherhost/module/conf.d'}, None, controller),
        ]
        cases += [({'src': src}, None, 'root directory') for src in ('/', '//', '/.', '/./')]
        cases += [({'src': self.src + suffix}, None, "'..'") for suffix in ('/..', '/../', '/sub/../.', '/sub/..//./')]
        for args, delegate_to, msg in cases:
            with self.subTest(args=args, delegate_to=delegate_to):
                with patch.object(tempfile, 'mkdtemp', side_effect=AssertionError('staging')):
                    x, result = self._run(delegate_to=delegate_to, **args)
                self._assert_refused(x, result, msg)

    def test_decrypt_refuses_symlink_src(self):
        self._encrypt()
        os.symlink(self.src, os.path.join(self.tmpdir, 'alias'))
        os.symlink('etc/conf.d', os.path.join(self.tmpdir, 'relative_alias'))
        self._symlink('secret.yml', 'link.yml')
        self._symlink('missing', 'dangling')
        srcs = [os.path.join(self.tmpdir, 'alias'), os.path.join(self.tmpdir, 'relative_alias'),
                os.path.join(self.src, 'link.yml'), os.path.join(self.src, 'dangling'), os.path.join(self.tmpdir, 'alias', 'sub', '..', 'link.yml')]
        for src in srcs:
            for kwargs in ({}, {'copy_links': True}):
                with self.subTest(src=src, kwargs=kwargs):
                    x, result = self._run(src=src, **kwargs)
                    self._assert_refused(x, result, 'symbolic link')
            with self.subTest(src=src, decrypt=False):
                x, result = self._run_without_decrypt(src=src)
                self._assert_succeeded(x, result)
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
            with self.subTest(local_tmp=local_tmp, src=src):
                with patch.object(C, 'DEFAULT_LOCAL_TMP', local_tmp), patch.object(tempfile, 'mkdtemp', side_effect=AssertionError('staging')):
                    x, result = self._run(src=src)
                self._assert_refused(x, result, 'local temporary directory')
                self.assertEqual(os.listdir(inner_tmp), [])

        with patch.object(C, 'DEFAULT_LOCAL_TMP', inner_tmp):
            x, result = self._run(src=self.src + '/plain_only/')
        self._assert_succeeded(x, result)

    def test_decrypt_refuses_src_with_environment_variable(self):
        self._encrypt()
        os.mkdir(os.path.join(self.tmpdir, '$SYNCHRONIZE_X'))
        with patch.dict(os.environ, {'SYNCHRONIZE_X': 'etc'}):
            for src in (os.path.join(self.tmpdir, '$SYNCHRONIZE_X', 'conf.d'), os.path.join(self.tmpdir, '${SYNCHRONIZE_X}', 'conf.d') + '/'):
                with self.subTest(src=src):
                    x, result = self._run(src=src)
                    self._assert_refused(x, result, 'environment variable')
                    x, result = self._run_without_decrypt(src=src)
                    self._assert_succeeded(x, result)
                    self.assertEqual(x.final_module_args['src'], src)

    def test_decrypt_preserves_group_when_owner_cannot_be_set(self):
        self._encrypt()
        self._symlink('secret.yml', 'link')
        groups = {}

        def lchown(path, uid, gid):
            if uid != -1:
                raise os_error(errno.EPERM)
            groups[os.path.normpath(path)] = gid

        with patch.object(os, 'lchown', side_effect=lchown), patch.object(os, 'link', side_effect=os_error(errno.EXDEV)):
            x, result = self._run()
        self._assert_succeeded(x, result)
        staged_src = x.staging_dir + self.src
        for name in ('secret.yml', 'sub/deep/key.pem', 'plain.txt', 'link', 'sub', ''):
            with self.subTest(name=name):
                self.assertEqual(groups[os.path.normpath(os.path.join(staged_src, name))], os.lstat(os.path.join(self.src, name)).st_gid)
        self.assertEqual(groups[x.staging_dir + self.parent], os.stat(self.parent).st_gid)

    def test_decrypt_tolerates_chown_failure(self):
        self._encrypt()
        self._symlink('secret.yml', 'link')
        with patch.object(os, 'lchown', side_effect=os_error(errno.EPERM)) as lchown:
            x, result = self._run()
        self.assertTrue(lchown.called)
        self._assert_staged(x, result)

    def test_decrypt_staging_modes(self):
        self._encrypt()
        self.addCleanup(os.umask, os.umask(0))
        with patch.object(os, 'mkdir', wraps=os.mkdir) as mkdir, patch.object(os, 'open', wraps=os.open) as os_open:
            x, result = self._run()
        self._assert_staged(x, result)
        self.assertEqual(set(call[0][1] for call in mkdir.call_args_list), set([0o700]))
        created = [call[0] for call in os_open.call_args_list if call[0][1] & os.O_CREAT]
        self.assertTrue(created)
        for path, flags, mode in created:
            self.assertTrue(flags & os.O_EXCL, path)
            self.assertEqual(mode, 0o600, path)

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

        with patch.object(os, 'mkdir', side_effect=mkdir), patch.object(os, 'open', side_effect=os_open), \
                patch.object(os, 'symlink', side_effect=symlink), \
                patch.object(os, 'chown', side_effect=record(True)), patch.object(os, 'lchown', side_effect=record(False)) as lchown, \
                patch.object(os, 'chmod', side_effect=record(True)) as chmod, patch.object(os, 'utime', side_effect=record(True)) as utime:
            x, result = self._run()
        self._assert_succeeded(x, result)
        for mock in (lchown, chmod, utime):
            self.assertTrue(mock.called)
        for path, ino in changed:
            self.assertIn(ino, created, path)

    def test_decrypt_removes_staging_dir_when_module_raises(self):
        self._encrypt()
        for side_effect in (BreakPoint(), KeyboardInterrupt()):
            with self.subTest(side_effect=side_effect):
                x = DecryptTester(self.loader, execute_side_effect=side_effect)
                self.assertRaises(type(side_effect), x.run, self._args(decrypt=True))
                self.assertTrue(x.execute_called)
                self._assert_staged_tree(x.staged)
                self._assert_clean()

    def test_decrypt_staging_errors(self):
        self._encrypt()
        before = self._outside_local_tmp()
        for name in ('copystat', 'copyfileobj'):
            for side_effect in (BreakPoint(), KeyboardInterrupt(), os_error(errno.EACCES)):
                with self.subTest(name=name, side_effect=side_effect):
                    x = DecryptTester(self.loader)
                    with patch.object(shutil, name, side_effect=side_effect):
                        if isinstance(side_effect, OSError):
                            self._assert_failed(x, x.run(self._args(decrypt=True)), 'Failed to decrypt %s: ' % self.src)
                        else:
                            self.assertRaises(type(side_effect), x.run, self._args(decrypt=True))
                    self.assertFalse(x.execute_called)
                    self._assert_clean()
        self.assertEqual(self._outside_local_tmp(), before)

    def test_decrypt_file_names_with_special_characters(self):
        self._encrypt()
        for name in ('a$HOME.txt', '${HOME}', "'quoted'", '"double"', '~user', 'sp ace.txt'):
            self._write(name, b'plain\n', 0o644, 1500000005)
        self._write('$SYNCHRONIZE_UNDEFINED.yml', self.top_secret, 0o600, 1400000002)

        x, result = self._run()
        self._assert_staged(x, result, decrypted={
            'secret.yml': b'top secret\n', 'sub/deep/key.pem': b'deep secret\n', '$SYNCHRONIZE_UNDEFINED.yml': b'top secret\n'})

        src = os.path.join(self.src, '$SYNCHRONIZE_UNDEFINED.yml')
        x, result = self._run(src=src)
        self._assert_succeeded(x, result)
        self._assert_staged_src(x, src)
        self.assertEqual(x.staged['$SYNCHRONIZE_UNDEFINED.yml'].data, b'top secret\n')

    def test_decrypt_encrypted_file_name_with_variable(self):
        cases = (
            ('a$HOME.yml', {}, None),
            ('$SYNCHRONIZE_X.yml', {'SYNCHRONIZE_X': 'other'}, b'OTHER PLAIN\n'),
            ('$SYNCHRONIZE_X.yml', {'SYNCHRONIZE_X': 'other'}, self.deep_secret),
        )
        for name, environ, other in cases:
            with self.subTest(name=name, other=other):
                path = self._write(name, self.top_secret, 0o600, 1400000002)
                if other is not None:
                    self._write('other.yml', other, 0o644, 1400000003)
                self.loader.get_real_file.reset_mock()
                with patch.dict(os.environ, environ):
                    x, result = self._run()
                self._assert_failed(x, result, 'Failed to decrypt %s' % path)
                self.assertNotIn(path, self._decrypted_paths())
                if other != self.deep_secret:
                    self.assertEqual(self._decrypted_paths(), [])
                os.unlink(path)

    def test_decrypt_refuses_loader_result_outside_local_tmp(self):
        self._encrypt()
        other = self._write('other.yml', b'OTHER PLAIN\n', 0o644, 1400000003)
        outside = os.path.join(self._create_outside('outside.yml', b'OUTSIDE\n'), 'outside.yml')
        secret = os.path.join(self.src, 'secret.yml')
        for returned in (other, outside, secret):
            with self.subTest(returned=returned):
                loader = MagicMock()
                loader.path_dwim.side_effect = lambda path: path
                loader.get_real_file.return_value = returned
                x, result = self._run(loader=loader, src=secret)
                self._assert_failed(x, result, 'Failed to decrypt %s' % secret)
                self.assertFalse(loader.cleanup_tmp_file.called)
                self.assertTrue(os.path.exists(returned))

    def test_decrypt_removes_the_decrypted_file_of_the_loader(self):
        self._encrypt()
        self.loader.cleanup_tmp_file = MagicMock(wraps=self.loader.cleanup_tmp_file)
        x, result = self._run()
        self._assert_succeeded(x, result)
        self.assertEqual(self.loader.cleanup_tmp_file.call_count, 2)
        for call in self.loader.cleanup_tmp_file.call_args_list:
            self.assertEqual(os.path.dirname(call[0][0]), self.local_tmp)

    def test_decrypt_loader_error(self):
        self._encrypt()
        self._write('sub/broken.yml', self.other_secret, 0o600, 1400000002)
        x, result = self._run()
        self._assert_failed(x, result, 'Failed to decrypt %s: ' % os.path.join(self.src, 'sub', 'broken.yml'))

    def test_decrypt_without_vault_secret(self):
        self._encrypt()
        x, result = self._run(loader=DataLoader())
        self._assert_failed(x, result, 'Failed to decrypt')

    @unittest.skipIf(os.geteuid() == 0, 'root can read every file')
    def test_decrypt_unreadable_file(self):
        self._encrypt()
        self._write('unreadable.txt', self.top_secret, 0o000, 1500000006)
        x, result = self._run()
        self._assert_staged(x, result)

        with patch.object(os, 'link', side_effect=os_error(errno.EXDEV)):
            x, result = self._run()
        self._assert_failed(x, result, 'Failed to decrypt')
        self.assertIn('unreadable.txt', result['msg'])

        unreadable = os.path.join(self.src, 'unreadable.txt')
        x, result = self._run(src=unreadable)
        self._assert_succeeded(x, result)
        self.assertEqual(x.final_module_args['src'], unreadable)

    @unittest.skipIf(os.geteuid() == 0, 'root can read every directory')
    def test_decrypt_unreadable_directory(self):
        self._encrypt()
        unreadable = os.path.join(self.src, 'plain_only')
        os.chmod(unreadable, 0o000)
        self.addCleanup(os.chmod, unreadable, 0o700)
        for src in (self.src, self.src + '/', unreadable + '/'):
            with self.subTest(src=src):
                x, result = self._run(src=src)
                self._assert_failed(x, result, 'Failed to decrypt %s: the directory cannot be read' % unreadable)

        x = DecryptTester(self.loader)
        SAM = ActionModule(x.task, x.connection, x._play_context, self.loader, x.templar, x.shared_loader_obj)
        staging_dir = tempfile.mkdtemp(dir=self.local_tmp)
        encrypted = set([os.path.join(self.src, 'secret.yml')])
        try:
            self.assertRaises(AnsibleError, SAM._stage_src, self.src, staging_dir, encrypted)
        finally:
            SAM._remove_staging_dir(staging_dir)
        self._assert_clean()

    def test_decrypt_passes_rsync_options_through(self):
        self._encrypt()
        cases = (
            ({'rsync_opts': ['-R']}, None),
            ({'rsync_opts': ['--files-from=x']}, None),
            ({'rsync_opts': ['-L']}, None),
            ({'copy_links': True}, None),
            ({}, {'ansible_rsync_path': '/usr/bin/rsync --relative'}),
        )
        for args, task_vars in cases:
            with self.subTest(args=args, task_vars=task_vars):
                expected = DecryptTester(None)
                expected.run(self._args(**args), task_vars=task_vars)
                x, result = self._run(task_vars=task_vars, **args)
                self._assert_staged(x, result)
                self.assertIs(x.final_module_args.pop('decrypt'), True)
                x.final_module_args['src'] = self.src
                self.assertEqual(x.final_module_args, expected.final_module_args)
                if task_vars:
                    self.assertEqual(x.final_module_args['_local_rsync_path'], task_vars['ansible_rsync_path'])
