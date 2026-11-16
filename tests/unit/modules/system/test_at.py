from __future__ import absolute_import, division, print_function

__metaclass__ = type

import os
import pwd
import tempfile

import pytest

from ansible_collections.ansible.posix.tests.unit.compat.mock import MagicMock, patch

from ansible_collections.ansible.posix.plugins.modules import at


@pytest.fixture
def module(tmp_path):
    module = MagicMock(name='AnsibleModule')
    module.tmpdir = str(tmp_path / 'ansible-moduletmp')
    os.mkdir(module.tmpdir)
    module.run_command.return_value = (0, '', '')
    return module


def test_add_job_leaves_module_tmpdir(module):
    with patch('os.getcwd', return_value=module.tmpdir):
        at.add_job(module, {}, '/usr/bin/at', 1, 'minutes', None, '/tmp/atjob')

    cwd = module.run_command.call_args[1]['cwd']
    assert cwd == pwd.getpwuid(os.geteuid()).pw_dir


def test_add_job_keeps_other_cwd(module):
    with patch('os.getcwd', return_value=tempfile.gettempdir()):
        at.add_job(module, {}, '/usr/bin/at', 1, 'minutes', None, '/tmp/atjob')

    assert module.run_command.call_args[1].get('cwd') is None


def test_add_job_falls_back_to_root(module):
    with patch('os.getcwd', return_value=module.tmpdir), patch('os.access', return_value=False):
        at.add_job(module, {}, '/usr/bin/at', 1, 'minutes', None, '/tmp/atjob')

    assert module.run_command.call_args[1]['cwd'] == '/'
