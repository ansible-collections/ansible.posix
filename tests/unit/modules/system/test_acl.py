# -*- coding: utf-8 -*-
# Copyright: Contributors to the Ansible project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

import json

import pytest

from ansible.module_utils import basic
from ansible.module_utils.common.text.converters import to_bytes

from ansible_collections.ansible.posix.plugins.modules import acl


class FailJson(Exception):
    pass


def fail_json(*args, **kwargs):
    raise FailJson(kwargs)


def run_acl_main(monkeypatch, tmp_path, **params):
    params.setdefault('path', str(tmp_path))
    params.update({'_ansible_remote_tmp': str(tmp_path), '_ansible_keep_remote_files': False})
    args = json.dumps({'ANSIBLE_MODULE_ARGS': params})
    try:
        from ansible.module_utils.testing import patch_module_args
    except ImportError:
        monkeypatch.setattr(basic, '_ANSIBLE_ARGS', to_bytes(args))
        patcher = None
    else:
        patcher = patch_module_args(params)
    monkeypatch.setattr(basic.AnsibleModule, 'fail_json', fail_json)
    monkeypatch.setattr(acl.platform, 'system', lambda: 'Linux')
    # nfs4_setfacl must never be run in these tests.
    monkeypatch.setattr(acl, 'run_acl', lambda *a, **kw: pytest.fail('run_acl called'))
    with pytest.raises(FailJson) as exc:
        if patcher is None:
            acl.main()
        else:
            with patcher:
                acl.main()
    return exc.value.args[0]


@pytest.mark.parametrize('state', ['present', 'absent'])
def test_nfsv4_without_permissions_fails_cleanly(monkeypatch, tmp_path, state):
    result = run_acl_main(
        monkeypatch, tmp_path,
        etype='user', entity='nobody', state=state, use_nfsv4_acls=True,
    )
    assert result['msg'] == "'permissions' MUST be set when 'use_nfsv4_acls=true' and 'state=%s'." % state


def test_nfsv4_entry_without_permissions_fails_cleanly(monkeypatch, tmp_path):
    result = run_acl_main(
        monkeypatch, tmp_path,
        entry='user:nobody', state='absent', use_nfsv4_acls=True,
    )
    assert result['msg'] == "'permissions' MUST be set when 'use_nfsv4_acls=true' and 'state=absent'."
