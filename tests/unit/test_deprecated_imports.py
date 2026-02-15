from __future__ import absolute_import, division, print_function

__metaclass__ = type

import os
import re

from ansible_collections.ansible.posix.tests.unit.compat import unittest


# Deprecated import patterns that trigger warnings on ansible-core >= 2.20
# and will be removed in ansible-core 2.24.
DEPRECATED_PATTERNS = [
    (
        re.compile(r'from ansible\.module_utils\._text import'),
        'from ansible.module_utils.common.text.converters import',
    ),
    (
        re.compile(r'from ansible\.module_utils\.common\._collections_compat import'),
        'from collections.abc import',
    ),
]


def _get_collection_root():
    """Return the root directory of this collection."""
    # tests/unit/test_deprecated_imports.py -> collection root
    return os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def _find_python_files(root):
    """Yield all .py files under root."""
    for dirpath, _dirnames, filenames in os.walk(root):
        for filename in filenames:
            if filename.endswith('.py'):
                yield os.path.join(dirpath, filename)


class TestNoDeprecatedImports(unittest.TestCase):

    def test_no_deprecated_module_utils_imports(self):
        """Ensure no files use deprecated ansible.module_utils import paths.

        ansible-core 2.20 deprecated ``ansible.module_utils._text`` (use
        ``ansible.module_utils.common.text.converters``) and
        ``ansible.module_utils.common._collections_compat`` (use
        ``collections.abc``). Both will be removed in ansible-core 2.24.
        """
        root = _get_collection_root()
        violations = []

        for filepath in _find_python_files(root):
            relpath = os.path.relpath(filepath, root)
            with open(filepath, 'r') as f:
                for lineno, line in enumerate(f, 1):
                    for pattern, replacement in DEPRECATED_PATTERNS:
                        if pattern.search(line):
                            violations.append(
                                '%s:%d: deprecated import found:\n'
                                '  %s\n'
                                '  replace with: %s'
                                % (relpath, lineno, line.rstrip(), replacement)
                            )

        if violations:
            self.fail(
                'Found deprecated imports that will break on ansible-core 2.24:\n\n'
                + '\n\n'.join(violations)
            )
