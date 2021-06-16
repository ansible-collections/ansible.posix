#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2014, Richard Isaacson <richard.c.isaacson@gmail.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type


DOCUMENTATION = r'''
---
module: at
short_description: Schedule the execution of a command or script file via the at command
description:
 - Use this module to schedule a command or script file to run once in the future.
 - All jobs are executed in the 'a' queue.
version_added: "1.0.0"
options:
  chdir:
    description:
    - An optional location from where to run the command at. Useful for intance
      when running a playbook using ansible-pull with C(purge) option.
    type: path
    version_added: 1.1.2
  command:
    description:
     - A command to be executed in the future.
    type: str
  script_file:
    description:
     - An existing script file to be executed in the future.
    type: str
  count:
    description:
     - The count of units in the future to execute the command or script file.
    type: int
  units:
    description:
     - The type of units in the future to execute the command or script file.
    type: str
    choices: [ minutes, hours, days, weeks ]
  state:
    description:
     - The state dictates if the command or script file should be evaluated as present(added) or absent(deleted).
    type: str
    choices: [absent, present]
    default: present
  unique:
    description:
     - If a matching job is present a new job will not be added.
    type: bool
    default: no
requirements:
 - at
author:
- Richard Isaacson (@risaacson)
'''

EXAMPLES = r'''
- name: Schedule a command to execute in 20 minutes as root
  ansible.posix.at:
    command: ls -d / >/dev/null
    count: 20
    units: minutes

- name: Match a command to an existing job and delete the job
  ansible.posix.at:
    command: ls -d / >/dev/null
    state: absent

- name: Schedule a command to execute in 20 minutes making sure it is unique in the queue
  ansible.posix.at:
    command: ls -d / >/dev/null
    count: 20
    units: minutes
    unique: yes
'''

import os
import platform
import tempfile

from ansible.module_utils.basic import AnsibleModule


def add_job(module, result, at_cmd, count, units, command, script_file, chdir=None):
    at_command = "%s -f %s now + %s %s" % (at_cmd, script_file, count, units)
    rc, out, err = module.run_command(at_command, cwd=chdir, check_rc=True)
    if command:
        os.unlink(script_file)
    result['changed'] = True


def delete_job(module, result, at_cmd, command, script_file, chdir=None):
    for matching_job in get_matching_jobs(module, at_cmd, script_file):
        at_command = "%s -r %s" % (at_cmd, matching_job)
        rc, out, err = module.run_command(at_command, cwd=chdir, check_rc=True)
        result['changed'] = True
    if command:
        os.unlink(script_file)
    module.exit_json(**result)


def get_matching_jobs(module, at_cmd, script_file, chdir=None):
    matching_jobs = []

    atq_cmd = module.get_bin_path('atq', True)

    # Get list of job numbers for the user.
    atq_command = "%s" % atq_cmd
    rc, out, err = module.run_command(atq_command, cwd=chdir, check_rc=True)
    current_jobs = out.splitlines()
    if len(current_jobs) == 0:
        return matching_jobs

    # Read script_file into a string.
    with open(script_file) as script_fh:
        script_file_string = script_fh.read().strip()

    # Loop through the jobs.
    #   If the script text is contained in a job add job number to list.
    for current_job in current_jobs:
        split_current_job = current_job.split()
        at_opt = '-c' if platform.system() != 'AIX' else '-lv'
        at_command = "%s %s %s" % (at_cmd, at_opt, split_current_job[0])
        rc, out, err = module.run_command(at_command, cwd=chdir, check_rc=True)
        if script_file_string in out:
            matching_jobs.append(split_current_job[0])

    # Return the list.
    return matching_jobs


def create_tempfile(command):
    filed, script_file = tempfile.mkstemp(prefix='at')
    fileh = os.fdopen(filed, 'w')
    fileh.write(command + os.linesep)
    fileh.close()
    return script_file


def main():

    module = AnsibleModule(
        argument_spec=dict(
            command=dict(type='str'),
            chdir=dict(type='path'),
            script_file=dict(type='str'),
            count=dict(type='int'),
            units=dict(type='str', choices=['minutes', 'hours', 'days', 'weeks']),
            state=dict(type='str', default='present', choices=['absent', 'present']),
            unique=dict(type='bool', default=False),
        ),
        mutually_exclusive=[['command', 'script_file']],
        required_one_of=[['command', 'script_file']],
        supports_check_mode=False,
    )

    at_cmd = module.get_bin_path('at', True)

    chdir = module.params['chdir']
    command = module.params['command']
    script_file = module.params['script_file']
    count = module.params['count']
    units = module.params['units']
    state = module.params['state']
    unique = module.params['unique']

    if (state == 'present') and (not count or not units):
        module.fail_json(msg="present state requires count and units")

    result = dict(
        changed=False,
        state=state,
    )

    # If command transform it into a script_file
    if command:
        script_file = create_tempfile(command)

    # if absent remove existing and return
    if state == 'absent':
        delete_job(module, result, at_cmd, command, script_file, chdir=chdir)

    # if unique if existing return unchanged
    if unique:
        if len(get_matching_jobs(module, at_cmd, script_file)) != 0:
            if command:
                os.unlink(script_file)
            module.exit_json(**result)

    result['script_file'] = script_file
    result['count'] = count
    result['units'] = units

    add_job(module, result, at_cmd, count, units, command, script_file,
            chdir=chdir)

    module.exit_json(**result)


if __name__ == '__main__':
    main()
