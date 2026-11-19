# Copyright (c) 2026 Ansible Project
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import absolute_import, division, print_function
__metaclass__ = type

from ansible_collections.ansible.posix.plugins.modules.authorized_key import parseoptions, parsekey


def test_parseoptions_trailing_and_leading_whitespace():
    # Issue #327: trailing whitespace on options should be stripped
    options = 'command="borg serve --append-only --restrict-to-path /home/borg-user/backup",restrict '
    parsed = parseoptions(None, options)
    items = dict(parsed.items())
    assert "restrict" in items
    assert "restrict " not in items
    assert items["restrict"] is None
    assert items["command"] == '"borg serve --append-only --restrict-to-path /home/borg-user/backup"'


def test_parseoptions_spaces_around_commas():
    # Options with spaces around comma separator
    options = 'no-port-forwarding, from="10.0.1.1", no-agent-forwarding'
    parsed = parseoptions(None, options)
    items = dict(parsed.items())
    assert "no-port-forwarding" in items
    assert "from" in items
    assert " from" not in items
    assert items["from"] == '"10.0.1.1"'
    assert "no-agent-forwarding" in items


def test_parseoptions_spaces_around_equals():
    # Options with whitespace around equals sign
    options = 'from = "10.0.1.1", environment = "NAME=value"'
    parsed = parseoptions(None, options)
    items = dict(parsed.items())
    assert items["from"] == '"10.0.1.1"'
    assert items["environment"] == '"NAME=value"'


def test_parsekey_with_options_matches_cleaned_key_options():
    key_line = 'command="echo hi",restrict ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIP9Z7HlUQ0Dk user@example.com'
    existing = parsekey(None, key_line)
    existing_options = existing[2]

    # User specifies key_options with trailing whitespace
    user_options = parseoptions(None, 'command="echo hi",restrict ')
    assert list(user_options.items()) == list(existing_options.items())
