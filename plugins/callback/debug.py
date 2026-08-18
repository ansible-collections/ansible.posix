# (c) 2017 Ansible Project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = '''
    name: debug
    type: stdout
    short_description: formatted stdout/stderr display
    description:
      - Use this callback to sort through extensive debug output
    extends_documentation_fragment:
      - default_callback
    requirements:
      - set as stdout in configuration
'''

from ansible import constants as C
from ansible import context
from ansible.plugins.callback.default import CallbackModule as CallbackModule_default
from ansible.utils.color import ANSIBLE_COLOR, colorize, stringc
from ansible.utils.display import get_text_width


def _text_width(text):
    try:
        return get_text_width(text)
    except EnvironmentError:
        return len(text)


class CallbackModule(CallbackModule_default):  # pylint: disable=too-few-public-methods,no-init
    '''
    Override for the default callback module.

    Render std err/out outside of the rest of the result which it prints with
    indentation.
    '''
    CALLBACK_VERSION = 2.0
    CALLBACK_TYPE = 'stdout'
    CALLBACK_NAME = 'ansible.posix.debug'

    def _dump_results(self, result, indent=None, sort_keys=True, keep_invocation=False):
        '''Return the text to output for a result.'''

        # Enable JSON identation
        result['_ansible_verbose_always'] = True

        save = {}
        for key in ['stdout', 'stdout_lines', 'stderr', 'stderr_lines', 'msg', 'module_stdout', 'module_stderr']:
            if key in result:
                save[key] = result.pop(key)

        output = CallbackModule_default._dump_results(self, result)

        for key in ['stdout', 'stderr', 'msg', 'module_stdout', 'module_stderr']:
            if key in save and save[key]:
                output += '\n\n%s:\n\n%s\n' % (key.upper(), save[key])

        for key, value in save.items():
            result[key] = value

        return output

    def _format_host_field(self, host, task_stats, width, color=True):
        if color and ANSIBLE_COLOR:
            if task_stats['failures'] != 0 or task_stats['unreachable'] != 0:
                host_text = stringc(host, C.COLOR_ERROR)
            elif task_stats['changed'] != 0:
                host_text = stringc(host, C.COLOR_CHANGED)
            else:
                host_text = stringc(host, C.COLOR_OK)
        else:
            host_text = host

        padding = max(0, width - _text_width(host))
        return u"%s%s" % (host_text, u' ' * padding)

    def _play_recap_line(self, host, task_stats, host_width, color=True):
        return u"%s : %s %s %s %s %s %s %s" % (
            self._format_host_field(host, task_stats, host_width, color=color),
            colorize(u'ok', task_stats['ok'], C.COLOR_OK if color else None),
            colorize(u'changed', task_stats['changed'], C.COLOR_CHANGED if color else None),
            colorize(u'unreachable', task_stats['unreachable'], C.COLOR_UNREACHABLE if color else None),
            colorize(u'failed', task_stats['failures'], C.COLOR_ERROR if color else None),
            colorize(u'skipped', task_stats['skipped'], C.COLOR_SKIP if color else None),
            colorize(u'rescued', task_stats['rescued'], C.COLOR_OK if color else None),
            colorize(u'ignored', task_stats['ignored'], C.COLOR_WARN if color else None),
        )

    def v2_playbook_on_stats(self, stats):
        self._display.banner("PLAY RECAP")

        hosts = sorted(stats.processed.keys())
        host_width = max((_text_width(h) for h in hosts), default=0)

        for host in hosts:
            task_stats = stats.summarize(host)
            self._display.display(
                self._play_recap_line(host, task_stats, host_width, color=True),
                screen_only=True,
            )
            self._display.display(
                self._play_recap_line(host, task_stats, host_width, color=False),
                log_only=True,
            )

        self._display.display("", screen_only=True)

        if stats.custom and self.get_option('show_custom_stats'):
            self._display.banner("CUSTOM STATS: ")
            for key in sorted(stats.custom.keys()):
                if key == '_run':
                    continue
                self._display.display('\t%s: %s' % (key, self._dump_results(stats.custom[key], indent=1).replace('\n', '')))

            if '_run' in stats.custom:
                self._display.display("", screen_only=True)
                self._display.display('\tRUN: %s' % self._dump_results(stats.custom['_run'], indent=1).replace('\n', ''))
            self._display.display("", screen_only=True)

        if context.CLIARGS['check'] and self.get_option('check_mode_markers'):
            self._display.banner("DRY RUN")
