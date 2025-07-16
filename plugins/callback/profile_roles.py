# (c) 2017, Tennis Smith, https://github.com/gamename
# (c) 2017 Ansible Project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

# Make coding more python3-ish
from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = '''
    name: profile_roles
    type: aggregate
    short_description: adds timing information to roles
    description:
        - This callback module provides profiling for ansible roles.
    requirements:
      - whitelisting in configuration
    options:
      summary_only:
        description:
          - Only show summary, not individual task profiles.
            Especially usefull in combination with C(DISPLAY_SKIPPED_HOSTS=false) and/or C(ANSIBLE_DISPLAY_OK_HOSTS=false).
        type: bool
        default: False
        env:
          - name: PROFILE_ROLES_SUMMARY_ONLY
        ini:
          - section: callback_profile_roles
            key: summary_only
        version_added: 1.5.0
      datetime_format:
        description:
          - Datetime format, as expected by the C(strftime) and C(strptime) methods.
            An C(iso8601) alias will be translated to C('%Y-%m-%dT%H:%M:%S.%f') if that datetime standard wants to be used.
        default: '%A %d %B %Y  %H:%M:%S %z'
        env:
          - name: PROFILE_ROLES_FORMAT
        ini:
          - section: callback_profile_roles
            key: datetime_format
        version_added: 3.0.0
'''

import collections
import time

from ansible.plugins.callback import CallbackBase
from ansible.module_utils.six.moves import reduce
from datetime import datetime


# define start time
dt0 = dtn = datetime.now().astimezone()


def secondsToStr(t):
    # http://bytes.com/topic/python/answers/635958-handy-short-cut-formatting-elapsed-time-floating-point-seconds
    def rediv(ll, b):
        return list(divmod(ll[0], b)) + ll[1:]

    return "%d:%02d:%02d.%03d" % tuple(
        reduce(rediv, [[t * 1000, ], 1000, 60, 60]))


def filled(msg, fchar="*"):
    if len(msg) == 0:
        width = 79
    else:
        msg = "%s " % msg
        width = 79 - len(msg)
    if width < 3:
        width = 3
    filler = fchar * width
    return "%s%s " % (msg, filler)


def timestamp(self):
    if self.current is not None:
        self.stats[self.current] = (datetime.now().astimezone() - self.stats[self.current]).total_seconds()
        self.totals[self.current] += self.stats[self.current]

def tasktime(self):
    global dtn
    cdtn = datetime.now().astimezone()
    datetime_current = cdtn.strftime(self.datetime_format)
    time_elapsed = secondsToStr((cdtn - dtn).total_seconds())
    time_total_elapsed = secondsToStr((cdtn - dt0).total_seconds())
    dtn = cdtn
    return filled('%s (%s)%s%s' %
                  (datetime_current, time_elapsed, ' ' * 7, time_total_elapsed))


class CallbackModule(CallbackBase):
    """
    This callback module provides profiling for ansible roles.
    """
    CALLBACK_VERSION = 2.0
    CALLBACK_TYPE = 'aggregate'
    CALLBACK_NAME = 'ansible.posix.profile_roles'
    CALLBACK_NEEDS_WHITELIST = True

    def __init__(self):
        self.stats = collections.Counter()
        self.totals = collections.Counter()
        self.current = None

        self.summary_only = None
        self.datetune_format = None

        super(CallbackModule, self).__init__()

    def set_options(self, task_keys=None, var_options=None, direct=None):

        super(CallbackModule, self).set_options(task_keys=task_keys, var_options=var_options, direct=direct)

        self.summary_only = self.get_option('summary_only')
        self.datetime_format = self.get_option('datetime_format')
        if self.datetime_format is not None:
            if self.datetime_format == 'iso8601':
                self.datetime_format = '%Y-%m-%dT%H:%M:%S.%f'

    def _display_tasktime(self):
        if not self.summary_only:
            self._display.display(tasktime(self))

    def _record_task(self, task):
        """
        Logs the start of each task
        """
        self._display_tasktime()
        timestamp(self)

        if task._role:
            self.current = task._role._role_name
        else:
            self.current = task.action

        self.stats[self.current] = datetime.now().astimezone()

    def v2_playbook_on_task_start(self, task, is_conditional):
        self._record_task(task)

    def v2_playbook_on_handler_task_start(self, task):
        self._record_task(task)

    def v2_playbook_on_stats(self, stats):
        # Align summary report header with other callback plugin summary
        self._display.banner("ROLES RECAP")

        self._display.display(tasktime(self))
        self._display.display(filled("", fchar="="))

        timestamp(self)
        total_time = sum(self.totals.values())

        # Print the timings starting with the largest one
        for result in self.totals.most_common():
            msg = u"{0:-<70}{1:->9}".format(result[0] + u' ', u' {0:.02f}s'.format(result[1]))
            self._display.display(msg)

        msg_total = u"{0:-<70}{1:->9}".format(u'total ', u' {0:.02f}s'.format(total_time))
        self._display.display(filled("", fchar="~"))
        self._display.display(msg_total)
