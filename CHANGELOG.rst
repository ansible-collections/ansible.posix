===========================
ansible.posix Release Notes
===========================

.. contents:: Topics


v1.5.4
======

Minor Changes
-------------

- json and jsonl - Add the ``ANSIBLE_JSON_INDENT`` parameter
- json and jsonl - Add the ``path`` attribute into the play and task output

Security Fixes
--------------

- firewalld - fix variable scope issue that lead to permanent transactions enabling all ports to be opened on specified protocol

Bugfixes
--------

- Support new sanity test for the ansible-core devel branch CI test (https://github.com/ansible-collections/ansible.posix/issues/446).
- firewall - Fix issue where adding an interface to a zone would fail when the daemon is offline
- firewall - Fix issue where opening a specific port resulted in opening the whole protocol of the specified port
- firewalld - Consider value of masquerade and icmp_block_inversion parameters when a boolean like value is passed

v1.5.2
======

Release Summary
---------------

This is the minor release of the ``ansible.posix`` collection.
This changelog contains all changes to the modules and plugins
in this collection that have been added after the release of
``ansible.posix`` 1.5.1.

Minor Changes
-------------

- Add jsonl callback plugin to ansible.posix collection
- firewalld - add `protocol` parameter

Bugfixes
--------

- Fixed a bug where firewalld module fails to create/remove zones when the daemon is stopped
- rhel_facts - Call exit_json with all keyword arguments

v1.5.1
======

Minor Changes
-------------

- mount - Add ``absent_from_fstab`` state (https://github.com/ansible-collections/ansible.posix/pull/166).
- mount - Add ``ephemeral`` value for the ``state`` parameter, that allows to mount a filesystem without altering the ``fstab`` file (https://github.com/ansible-collections/ansible.posix/pull/267).
- r4e_rpm_ostree - new module for validating package state on RHEL for Edge
- rhel_facts - new facts module to handle RHEL specific facts
- rhel_rpm_ostree - new module to handle RHEL rpm-ostree specific package management functionality
- rpm_ostree_upgrade - new module to automate rpm-ostree upgrades
- rpm_ostree_upgrade - new module to manage upgrades for rpm-ostree based systems

Bugfixes
--------

- Removed contentious terminology to match reference documentation in profile_tasks.
- firewall - Fixed to output a more complete missing library message.
- synchronize - Fixed hosts involved in rsync require the same password

v1.4.0
======

Release Summary
---------------

This is the minor release of the ``ansible.posix`` collection.
This changelog contains all changes to the modules in this collection that
have been added after the release of ``ansible.posix`` 1.3.0.

Minor Changes
-------------

- firewalld - Show warning message that variable type of ``masquerade`` and ``icmp_block_inversion`` will be changed from ``str`` to ``boolean`` in the future release (https://github.com/ansible-collections/ansible.posix/pull/254).
- selinux - optionally update kernel boot params when disabling/re-enabling SELinux (https://github.com/ansible-collections/ansible.posix/pull/142).

Bugfixes
--------

- Fix for whitespace in source full path causing error ```code 23) at main.c(1330) [sender=3.2.3]``` (https://github.com/ansible-collections/ansible.posix/pull/278)
- Include ``PSF-license.txt`` file for ``plugins/module_utils/_version.py``.
- Use vendored version of ``distutils.version`` instead of the deprecated Python standard library to address PEP 632 (https://github.com/ansible-collections/ansible.posix/issues/303).
- firewalld - Correct usage of queryForwardPort (https://github.com/ansible-collections/ansible.posix/issues/247).
- firewalld - Refine the handling of exclusive options (https://github.com/ansible-collections/ansible.posix/issues/255).
- mount - add a newline at the end of line in ``fstab`` (https://github.com/ansible-collections/ansible.posix/issues/210).
- profile_tasks - Correctly calculate task execution time with serial execution (https://github.com/ansible-collections/ansible.posix/issues/83).
- seboolean - add ``python3-libsemanage`` package dependency for RHEL8+ systems.

v1.3.0
======

Release Summary
---------------

This is the minor release of the ``ansible.posix`` collection.
This changelog contains all changes to the modules in this collection that
have been added after the release of ``ansible.posix`` 1.2.0.

Minor Changes
-------------

- acl - add new alias ``recurse`` for ``recursive`` parameter (https://github.com/ansible-collections/ansible.posix/issues/124).
- added 2.11 branch to test matrix, added ignore-2.12.txt.
- authorized_key - add ``no_log=False`` in ``argument_spec`` to clear false-positives of ``no-log-needed`` (https://github.com/ansible-collections/ansible.posix/pull/156).
- authorized_key - add a list of valid key types (https://github.com/ansible-collections/ansible.posix/issues/134).
- mount - Change behavior of ``boot`` option to set ``noauto`` on BSD nodes (https://github.com/ansible-collections/ansible.posix/issues/28).
- mount - Change behavior of ``boot`` option to set ``noauto`` on Linux nodes (https://github.com/ansible-collections/ansible.posix/issues/28).
- mount - add ``no_log=False`` in ``argument_spec`` to clear false-positives of ``no-log-needed`` (https://github.com/ansible-collections/ansible.posix/pull/156).
- mount - returns ``backup_file`` value when a backup fstab is created.
- synchronize - add ``delay_updates`` option (https://github.com/ansible-collections/ansible.posix/issues/157).
- synchronize - fix typo (https://github.com/ansible-collections/ansible.posix/pull/198).

Bugfixes
--------

- Synchronize module not recognizing remote ssh key (https://github.com/ansible-collections/ansible.posix/issues/24).
- Synchronize not using quotes around arguments like --out-format (https://github.com/ansible-collections/ansible.posix/issues/190).
- at - append line-separator to the end of the ``command`` (https://github.com/ansible-collections/ansible.posix/issues/169).
- csh - define ``ECHO`` and ``COMMAND_SEP`` (https://github.com/ansible-collections/ansible.posix/issues/204).
- firewalld - enable integration after migration (https://github.com/ansible-collections/ansible.posix/pull/239).
- firewalld - ensure idempotency with firewalld 0.9.3 (https://github.com/ansible-collections/ansible.posix/issues/179).
- firewalld - fix setting zone target to ``%%REJECT%%`` (https://github.com/ansible-collections/ansible.posix/pull/215).
- mount - Handle ``boot`` option on Solaris correctly (https://github.com/ansible-collections/ansible.posix/issues/184).
- synchronize - add ``community.podman.podman`` to the list of supported connection plugins (https://github.com/ansible-community/molecule-podman/issues/45).
- synchronize - complete podman support for synchronize module.
- synchronize - properly quote rsync CLI parameters (https://github.com/ansible-collections/ansible.posix/pull/241).
- synchronize - replace removed ``ansible_ssh_user`` by ``ansible_user`` everywhere; do the same for ``ansible_ssh_port`` and ``ansible_ssh_host`` (https://github.com/ansible-collections/ansible.posix/issues/60).
- synchronize - use SSH args from SSH connection plugin (https://github.com/ansible-collections/ansible.posix/issues/222).
- synchronize - use become_user when invoking rsync on remote with sudo (https://github.com/ansible-collections/ansible.posix/issues/186).
- sysctl - modifying conditional check for docker to fix tests being skipped (https://github.com/ansible-collections/ansible.posix/pull/226).

v1.2.0
======

Release Summary
---------------

This is the minor release of the ``ansible.posix`` collection.
This changelog contains all changes to the modules in this collection that
have been added after the release of ``ansible.posix`` 1.1.0.

Minor Changes
-------------

- firewalld - bring the ``target`` feature back (https://github.com/ansible-collections/ansible.posix/issues/112).
- fix sanity test for various modules.
- synchronize - add the ``ssh_connection_multiplexing`` option to allow SSH connection multiplexing (https://github.com/ansible/ansible/issues/24365).

Bugfixes
--------

- at - add AIX support (https://github.com/ansible-collections/ansible.posix/pull/99).
- synchronize - add ``community.docker.docker`` to the list of supported transports (https://github.com/ansible-collections/ansible.posix/issues/132).
- synchronize - do not prepend PWD when path is in form user@server:path or server:path (https://github.com/ansible-collections/ansible.posix/pull/118).
- synchronize - fix for private_key overriding in synchronize module.
- sysctl - do not persist sysctl when value is invalid (https://github.com/ansible-collections/ansible.posix/pull/101).

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
