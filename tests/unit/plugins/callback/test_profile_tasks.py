from __future__ import absolute_import, division, print_function

__metaclass__ = type

from ansible_collections.ansible.posix.tests.unit.compat import unittest
from ansible.utils.display import get_text_width

from ansible_collections.ansible.posix.plugins.callback.profile_tasks import (
    filled,
    format_timing_row,
    pad_to_display_width,
    truncate_name,
)


class ProfileTasksDisplayTestCase(unittest.TestCase):

    COLUMNS = 79
    LINE_WIDTH = COLUMNS + 1
    # Reproducer from https://github.com/ansible-collections/ansible.posix/pull/773#issuecomment-5325694910
    MAINTAINER_ASCII_LONG = (
        '012345678901234567890123456789012345678901234567890'
        '12345678901234567890123456789'
    )
    MAINTAINER_CJK_LONG = (
        '零一二三四五六七八九零一二三四五六七八九'
        '零一二三四五六七八九零一二三四五六七八九'
    )
    ASCII_LONG = MAINTAINER_ASCII_LONG
    CJK_LONG = MAINTAINER_CJK_LONG

    def test_filled_banner_matches_display_width(self):
        line = filled('TASKS RECAP', self.COLUMNS)
        self.assertEqual(get_text_width(line), self.LINE_WIDTH)
        self.assertTrue(line.endswith('*'))

    def test_filled_separator_matches_display_width(self):
        line = filled('', self.COLUMNS, fchar='=')
        self.assertEqual(get_text_width(line), self.LINE_WIDTH)
        self.assertEqual(line, '=' * self.LINE_WIDTH)

    def test_truncate_name_shortens_ascii_to_display_width(self):
        truncated = truncate_name(self.ASCII_LONG, 71)
        self.assertLessEqual(get_text_width(truncated), 71)
        self.assertTrue(truncated.endswith('...'))

    def test_truncate_name_shortens_cjk_to_display_width(self):
        truncated = truncate_name(self.CJK_LONG, 71)
        self.assertLessEqual(get_text_width(truncated), 71)
        self.assertTrue(truncated.endswith('...'))

    def test_truncate_name_leaves_short_names_unchanged(self):
        short = 'Short task'
        self.assertEqual(truncate_name(short, 71), short)
        self.assertEqual(truncate_name(self.CJK_LONG[:5], 71), self.CJK_LONG[:5])

    def test_format_timing_row_ascii_fits_terminal_width(self):
        row = format_timing_row(self.ASCII_LONG, 0.01, self.COLUMNS, truncate=True)
        self.assertEqual(get_text_width(row), self.LINE_WIDTH)
        self.assertIn('0.01s', row)

    def test_format_timing_row_cjk_fits_terminal_width(self):
        row = format_timing_row(self.CJK_LONG, 0.01, self.COLUMNS, truncate=True)
        self.assertEqual(get_text_width(row), self.LINE_WIDTH)
        self.assertIn('0.01s', row)

    def test_maintainer_cjk_reproducer_fits_under_len_budget_but_not_display_width(self):
        self.assertEqual(len(self.MAINTAINER_CJK_LONG), 40)
        self.assertEqual(get_text_width(self.MAINTAINER_CJK_LONG), 80)
        self.assertGreater(len(self.MAINTAINER_CJK_LONG), 0)

    def test_maintainer_cjk_reproducer_truncates_with_ellipsis(self):
        truncated = truncate_name(self.MAINTAINER_CJK_LONG, 71)
        self.assertLessEqual(get_text_width(truncated), 71)
        self.assertTrue(truncated.endswith('...'))
        self.assertNotEqual(truncated, self.MAINTAINER_CJK_LONG)

    def test_maintainer_ascii_and_cjk_recap_rows_match_terminal_width(self):
        ascii_row = format_timing_row(
            self.MAINTAINER_ASCII_LONG, 0.01, self.COLUMNS, truncate=True,
        )
        cjk_row = format_timing_row(
            self.MAINTAINER_CJK_LONG, 0.01, self.COLUMNS, truncate=True,
        )
        self.assertEqual(get_text_width(ascii_row), self.LINE_WIDTH)
        self.assertEqual(get_text_width(cjk_row), self.LINE_WIDTH)
        self.assertIn('...', ascii_row)
        self.assertIn('...', cjk_row)

    def test_format_timing_row_uses_dash_padding_for_timing_field(self):
        row = format_timing_row('Short task', 0.01, self.COLUMNS, truncate=True)
        self.assertTrue(row.endswith('--- 0.01s'))
        self.assertEqual(get_text_width(row), self.LINE_WIDTH)

    def test_pad_to_display_width_handles_cjk(self):
        padded = pad_to_display_width(self.MAINTAINER_CJK_LONG[:5] + u' ', 71)
        self.assertEqual(get_text_width(padded), 71)
        self.assertTrue(padded.endswith('-'))

    def test_format_timing_row_cjk_timing_suffix_matches_ascii(self):
        ascii_row = format_timing_row(self.MAINTAINER_ASCII_LONG, 0.01, self.COLUMNS, truncate=True)
        cjk_row = format_timing_row(self.MAINTAINER_CJK_LONG, 0.01, self.COLUMNS, truncate=True)
        self.assertTrue(ascii_row.endswith('--- 0.01s'))
        self.assertTrue(cjk_row.endswith('--- 0.01s'))
        self.assertNotIn('----', cjk_row)
        self.assertEqual(
            get_text_width(ascii_row[:ascii_row.rindex('.')]),
            get_text_width(cjk_row[:cjk_row.rindex('.')]),
        )
