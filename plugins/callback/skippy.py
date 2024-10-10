# (c) 2012-2014, Michael DeHaan <michael.dehaan@gmail.com>
# (c) 2017 Ansible Project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

# Make coding more python3-ish
from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = '''
    name: skippy
    type: stdout
    requirements:
      - set as main display callback
    short_description: Ansible screen output that ignores skipped status
    deprecated:
      why: The 'default' callback plugin now supports this functionality
      removed_at_date: '2024-12-05'
      alternative: "'default' callback plugin with 'display_skipped_hosts = no' option"
    extends_documentation_fragment:
      - default_callback
    description:
      - This callback does the same as the default except it does not output skipped host/task/item status
'''

from ansible.plugins.callback.default import CallbackModule as CallbackModule_default


class CallbackModule(CallbackModule_default):

    '''
    This is the default callback interface, which simply prints messages
    to stdout when new callback events are received.
    '''

    CALLBACK_VERSION = 2.0
    CALLBACK_TYPE = 'stdout'
    CALLBACK_NAME = 'ansible.posix.skippy'

    def v2_runner_on_skipped(self, result):
        pass

    def v2_runner_item_on_skipped(self, result):
        pass
