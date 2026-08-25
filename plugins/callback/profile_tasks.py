# (C) 2016, Joel, https://github.com/jjshoe
# (C) 2015, Tom Paine, <github@aioue.net>
# (C) 2014, Jharrod LaFon, @JharrodLaFon
# (C) 2012-2013, Michael DeHaan, <michael.dehaan@gmail.com>
# (C) 2017 Ansible Project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

# Make coding more python3-ish
from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = '''
    name: profile_tasks
    type: aggregate
    short_description: adds time information to tasks
    description:
      - Ansible callback plugin for timing individual tasks and overall execution time.
      - "Mashup of 2 excellent original works: https://github.com/jlafon/ansible-profile,
         https://github.com/junaid18183/ansible_home/blob/master/ansible_plugins/callback_plugins/timestamp.py.old"
      - "Format: C(<task start timestamp>) C(<length of previous task>) C(<current elapsed playbook execution time>)"
      - It also lists the top/bottom time consuming tasks in the summary (configurable)
      - Before 2.4 only the environment variables were available for configuration.
    requirements:
      - enable in configuration - see examples section below for details.
    options:
      output_limit:
        description: Number of tasks to display in the summary
        default: 20
        env:
          - name: PROFILE_TASKS_TASK_OUTPUT_LIMIT
        ini:
          - section: callback_profile_tasks
            key: task_output_limit
      sort_order:
        description: Adjust the sorting output of summary tasks
        choices: ['descending', 'ascending', 'none']
        default: 'descending'
        env:
          - name: PROFILE_TASKS_SORT_ORDER
        ini:
          - section: callback_profile_tasks
            key: sort_order
      summary_only:
        description:
          - Only show summary, not individual task profiles.
            Especially usefull in combination with C(DISPLAY_SKIPPED_HOSTS=false) and/or C(ANSIBLE_DISPLAY_OK_HOSTS=false).
        type: bool
        default: False
        env:
          - name: PROFILE_TASKS_SUMMARY_ONLY
        ini:
          - section: callback_profile_tasks
            key: summary_only
        version_added: 1.5.0
      datetime_format:
        description:
          - Datetime format, as expected by the C(strftime) and C(strptime) methods.
            An C(iso8601) alias will be translated to C('%Y-%m-%dT%H:%M:%S.%f') if that datetime standard wants to be used.
        default: '%A %d %B %Y  %H:%M:%S %z'
        env:
          - name: PROFILE_TASKS_DATETIME_FORMAT
        ini:
          - section: callback_profile_tasks
            key: datetime_format
        version_added: 3.0.0
      truncate_task_names:
        description:
          - Truncate long task names in the TASKS RECAP summary with an ellipsis so rows stay within the terminal width.
        type: bool
        default: false
        env:
          - name: PROFILE_TASKS_TRUNCATE_TASK_NAMES
        ini:
          - section: callback_profile_tasks
            key: truncate_task_names
        version_added: 2.3.0
'''

EXAMPLES = '''
example: >
  To enable, add this to your ansible.cfg file in the defaults block
    [defaults]
    callbacks_enabled=ansible.posix.profile_tasks
sample output: >
#
#    TASK: [ensure messaging security group exists] ********************************
#    Thursday 11 June 2017  22:50:53 +0100 (0:00:00.721)       0:00:05.322 *********
#    ok: [localhost]
#
#    TASK: [ensure db security group exists] ***************************************
#    Thursday 11 June 2017  22:50:54 +0100 (0:00:00.558)       0:00:05.880 *********
#    changed: [localhost]
#
'''

import collections

from datetime import datetime

from functools import reduce
from ansible.plugins.callback import CallbackBase
from ansible.utils.display import get_text_width


# define start time
dt0 = dtn = datetime.now().astimezone()


def secondsToStr(t):
    # http://bytes.com/topic/python/answers/635958-handy-short-cut-formatting-elapsed-time-floating-point-seconds
    def rediv(ll, b):
        return list(divmod(ll[0], b)) + ll[1:]

    return "%d:%02d:%02d.%03d" % tuple(reduce(rediv, [[t * 1000, ], 1000, 60, 60]))


def filled(msg, columns, fchar="*"):
    """Fill to the same width as display.banner() (columns + 1)."""
    if not msg:
        return fchar * (columns + 1)
    try:
        msg_width = get_text_width(msg)
    except EnvironmentError:
        msg_width = len(msg)
    fill_len = columns - msg_width
    if fill_len < 3:
        fill_len = 3
    return "%s %s" % (msg, fchar * fill_len)


def _text_width(text):
    try:
        return get_text_width(text)
    except EnvironmentError:
        return len(text)


def truncate_name(name, width):
    if width <= 0:
        return name
    if _text_width(name) <= width:
        return name
    if width <= 3:
        return name[:width]
    ellipsis = '...'
    for end in range(len(name), 0, -1):
        candidate = name[:end] + ellipsis
        if _text_width(candidate) <= width:
            return candidate
    return ellipsis


def pad_to_display_width(text, width, fillchar='-'):
    current = _text_width(text)
    if current >= width:
        return text
    return text + fillchar * (width - current)


def format_timing_row(task_name, elapsed, columns, truncate=False):
    line_width = columns + 1
    time_field_width = 9
    name_field_width = line_width - time_field_width
    if truncate:
        task_name = truncate_name(task_name, name_field_width - 1)
    prefix = task_name + u' '
    gap = name_field_width - _text_width(prefix)
    if gap == 1:
        # A lone dash before the timing field looks like misaligned padding.
        left = prefix + u' '
    else:
        left = pad_to_display_width(prefix, name_field_width)
    timing = u' {0:.02f}s'.format(elapsed)
    return left + timing.rjust(time_field_width, u'-')


def timestamp(self):
    if self.current is not None:
        elapsed = (datetime.now().astimezone() - self.stats[self.current]['started']).total_seconds()
        self.stats[self.current]['elapsed'] += elapsed


def tasktime(self):
    global dtn
    cdtn = datetime.now().astimezone()
    datetime_current = cdtn.strftime(self.datetime_format)
    time_elapsed = secondsToStr((cdtn - dtn).total_seconds())
    time_total_elapsed = secondsToStr((cdtn - dt0).total_seconds())
    dtn = cdtn
    return filled(
        '%s (%s)%s%s' % (datetime_current, time_elapsed, ' ' * 7, time_total_elapsed),
        self._display.columns,
    )


class CallbackModule(CallbackBase):
    """
    This callback module provides per-task timing, ongoing playbook elapsed time
    and ordered list of top 20 longest running tasks at end.
    """
    CALLBACK_VERSION = 2.0
    CALLBACK_TYPE = 'aggregate'
    CALLBACK_NAME = 'ansible.posix.profile_tasks'
    CALLBACK_NEEDS_WHITELIST = True

    def __init__(self):
        self.stats = collections.OrderedDict()
        self.current = None

        self.sort_order = None
        self.summary_only = None
        self.task_output_limit = None
        self.datetime_format = None
        self.truncate_task_names = None

        super(CallbackModule, self).__init__()

    def set_options(self, task_keys=None, var_options=None, direct=None):

        super(CallbackModule, self).set_options(task_keys=task_keys, var_options=var_options, direct=direct)

        self.sort_order = self.get_option('sort_order')
        if self.sort_order is not None:
            if self.sort_order == 'ascending':
                self.sort_order = False
            elif self.sort_order == 'descending':
                self.sort_order = True
            elif self.sort_order == 'none':
                self.sort_order = None

        self.summary_only = self.get_option('summary_only')

        self.task_output_limit = self.get_option('output_limit')
        if self.task_output_limit is not None:
            if self.task_output_limit == 'all':
                self.task_output_limit = None
            else:
                self.task_output_limit = int(self.task_output_limit)

        self.datetime_format = self.get_option('datetime_format')
        if self.datetime_format is not None:
            if self.datetime_format == 'iso8601':
                self.datetime_format = '%Y-%m-%dT%H:%M:%S.%f'

        self.truncate_task_names = self.get_option('truncate_task_names')

    def _display_tasktime(self):
        if not self.summary_only:
            self._display.display(tasktime(self))

    def _record_task(self, task):
        """
        Logs the start of each task
        """
        self._display_tasktime()
        timestamp(self)

        # Record the start time of the current task
        # stats[TASK_UUID]:
        #   started: Current task start time. This value will be updated each time a task
        #            with the same UUID is executed when `serial` is specified in a playbook.
        #   elapsed: Elapsed time since the first serialized task was started
        self.current = task._uuid
        dtn = datetime.now().astimezone()
        if self.current not in self.stats:
            self.stats[self.current] = {'started': dtn, 'elapsed': 0.0, 'name': task.get_name()}
        else:
            self.stats[self.current]['started'] = dtn
        if self._display.verbosity >= 2:
            self.stats[self.current]['path'] = task.get_path()

    def v2_playbook_on_task_start(self, task, is_conditional):
        self._record_task(task)

    def v2_playbook_on_handler_task_start(self, task):
        self._record_task(task)

    def v2_playbook_on_stats(self, stats):
        columns = self._display.columns
        line_width = columns + 1
        self._display.display(filled("TASKS RECAP", columns))

        self._display.display(tasktime(self))
        self._display.display(filled("", columns, fchar="="))

        timestamp(self)
        self.current = None

        results = list(self.stats.items())

        # Sort the tasks by the specified sort
        if self.sort_order is not None:
            results = sorted(
                self.stats.items(),
                key=lambda x: x[1]['elapsed'],
                reverse=self.sort_order,
            )

        # Display the number of tasks specified or the default of 20
        results = list(results)[:self.task_output_limit]

        # Print the timings
        for uuid, result in results:
            msg = format_timing_row(
                result['name'],
                result['elapsed'],
                columns,
                truncate=self.truncate_task_names,
            )
            if 'path' in result:
                path_name = result['path']
                if self.truncate_task_names:
                    path_name = truncate_name(path_name, line_width - 1)
                msg += u"\n%s" % pad_to_display_width(path_name + u' ', line_width)
            self._display.display(msg)
