from __future__ import absolute_import, division, print_function

__metaclass__ = type

from ansible_collections.ansible.posix.tests.unit.compat import unittest
from ansible.utils.display import get_text_width

from ansible_collections.ansible.posix.plugins.callback.debug import CallbackModule


class DebugPlayRecapTestCase(unittest.TestCase):

    TASK_STATS = {
        'ok': 4,
        'changed': 0,
        'unreachable': 0,
        'failures': 0,
        'skipped': 0,
        'rescued': 0,
        'ignored': 0,
    }
    # Reproducer from https://github.com/ansible-collections/ansible.posix/pull/778
    HOSTS = [
        'eic-guacamole-desktop-test-target',
        'ext-korcsmaros-slk',
        'short',
    ]
    CJK_HOST = '零一二三四五六七八九'

    def setUp(self):
        self.callback = CallbackModule()

    def _stat_column(self, line):
        return get_text_width(line[:line.index('ok=')])

    def _host_width(self, hosts):
        return max((get_text_width(host) for host in hosts), default=0)

    def test_format_host_field_pads_short_hostname(self):
        host_width = self._host_width(self.HOSTS)
        field = self.callback._format_host_field('short', self.TASK_STATS, host_width, color=False)
        self.assertEqual(get_text_width(field), host_width)
        self.assertTrue(field.startswith('short'))

    def test_play_recap_lines_align_colons_for_mixed_hostname_lengths(self):
        host_width = self._host_width(self.HOSTS)
        columns = [
            self._stat_column(
                self.callback._play_recap_line(host, self.TASK_STATS, host_width, color=False),
            )
            for host in self.HOSTS
        ]
        self.assertEqual(len(set(columns)), 1)

    def test_play_recap_lines_align_colon_character_index_for_ascii_hostnames(self):
        host_width = self._host_width(self.HOSTS)
        columns = [
            line.index(':')
            for line in (
                self.callback._play_recap_line(host, self.TASK_STATS, host_width, color=False)
                for host in self.HOSTS
            )
        ]
        self.assertEqual(len(set(columns)), 1)

    def test_play_recap_longest_host_sets_field_width(self):
        host_width = self._host_width(self.HOSTS)
        longest = max(self.HOSTS, key=get_text_width)
        field = self.callback._format_host_field(longest, self.TASK_STATS, host_width, color=False)
        self.assertEqual(get_text_width(field), host_width)
        self.assertEqual(field, longest)

    def test_cjk_hostname_fits_len_budget_but_not_display_width(self):
        self.assertEqual(len(self.CJK_HOST), 10)
        self.assertEqual(get_text_width(self.CJK_HOST), 20)

    def test_play_recap_lines_align_colons_with_cjk_hostname(self):
        hosts = [self.CJK_HOST, 'short']
        host_width = self._host_width(hosts)
        columns = [
            self._stat_column(
                self.callback._play_recap_line(host, self.TASK_STATS, host_width, color=False),
            )
            for host in hosts
        ]
        self.assertEqual(len(set(columns)), 1)
