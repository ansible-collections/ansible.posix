===========================
ansible.posix Release Notes
===========================

.. contents:: Topics


v1.1.1
======

Minor Changes
-------------

- skippy - fixed the deprecation warning (by date) for skippy callback plugin

Bugfixes
--------

- Fix synchronize to work with renamed docker and buildah connection plugins.

v1.1.0
======

Minor Changes
-------------

- firewalld - add firewalld module to ansible.posix collection

v1.0.0
======

Major Changes
-------------

- Bootstrap Collection (https://github.com/ansible-collections/ansible.posix/pull/1).

Minor Changes
-------------

- CI should use devel (https://github.com/ansible-collections/ansible.posix/pull/6).
- Enable tests for at, patch and synchronize modules (https://github.com/ansible-collections/ansible.posix/pull/5).
- Enabled tags in galaxy.yml (https://github.com/ansible-collections/ansible.posix/issues/18).
- Migrate hacking/cgroup_perf_recap_graph.py to this collection, since the cgroup_perf_recap callback lives here.
- Remove license key from galaxy.yml.
- Remove sanity jobs from shippable (https://github.com/ansible-collections/ansible.posix/pull/43).
- Removed ANSIBLE_METADATA from all the modules.
- Revert "Enable at, patch and synchronize tests (https://github.com/ansible-collections/ansible.posix/pull/5)".
- Update EXAMPLES section in modules to use FQCN.
- Update README.md (https://github.com/ansible-collections/ansible.posix/pull/4/).

Bugfixes
--------

- Allow unsetting existing environment vars via environment by specifying a null value (https://github.com/ansible/ansible/pull/68236).
- Mount - Handle remount with new options (https://github.com/ansible/ansible/issues/59460).
- Profile_tasks - result was a odict_items which is not subscriptable, so the slicing was failing (https://github.com/ansible/ansible/issues/59059).
- Revert "mount - Check if src exists before mounted (ansible/ansible#61752)".
- Typecast results before use in profile_tasks callback (https://github.com/ansible/ansible/issues/69563).
- authorized_keys - Added FIDO2 security keys (https://github.com/ansible-collections/ansible.posix/issues/17).
- authorized_keys - fix inconsistent return value for check mode (https://github.com/ansible-collections/ansible.posix/issues/37)
- json callback - Fix host result to task references in the resultant JSON output for non-lockstep strategy plugins such as free (https://github.com/ansible/ansible/issues/65931)
- mount - fix issues with ismount module_util pathing for Ansible 2.9 (fixes https://github.com/ansible-collections/ansible.posix/issues/21)
- patch - fix FQCN usage for action plugin (https://github.com/ansible-collections/ansible.posix/issues/11)
- selinux - add missing configuration keys for /etc/selinux/config (https://github.com/ansible-collections/ansible.posix/issues/23)
- synchronize - fix FQCN usage for action plugin (https://github.com/ansible-collections/ansible.posix/issues/11)

New Modules
-----------

- acl - Set and retrieve file ACL information.
- at - Schedule the execution of a command or script file via the at command
- authorized_key - Adds or removes an SSH authorized key
- mount - Control active and configured mount points
- patch - Apply patch files using the GNU patch tool
- seboolean - Toggles SELinux booleans
- selinux - Change policy and state of SELinux
- synchronize - A wrapper around rsync to make common tasks in your playbooks quick and easy
- sysctl - Manage entries in sysctl.conf.
