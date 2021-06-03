#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2012, Red Hat, inc
# Copyright: (c) 2021, quidame <quidame@poivron.org>
# Written by Seth Vidal, based on the mount modules from salt and puppet
# Enhanced by quidame (swapon/swapoff support)
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type


DOCUMENTATION = r'''
---
module: mount
short_description: Control active and configured mount points
description:
  - This module controls active and configured mount points in C(/etc/fstab),
    as well as active and configured swap spaces.
author:
  - Ansible Core Team
  - Seth Vidal (@skvidal)
  - quidame (@quidame)
version_added: "1.0.0"
options:
  path:
    description:
      - Path to the mount point (e.g. C(/mnt/files)). Must be C(none) (or C(-)
        on Solaris) for swap spaces.
      - Before Ansible 2.3 this option was only usable as I(dest), I(destfile) and I(name).
    type: path
    required: true
    aliases: [ name ]
  src:
    description:
      - Device (or NFS volume, or something else) to be mounted on I(path).
      - Required when I(state) set to C(present) or C(mounted), or when I(fstype=swap).
    type: path
  fstype:
    description:
      - Filesystem type.
      - Required when I(state) is C(present) or C(mounted). Also required for
        any I(state) to properly handle swap spaces (and then set to c(swap)).
    type: str
  opts:
    description:
      - Mount options (see fstab(5), or vfstab(4) on Solaris) for mountable
        filesystems, or swapon(8) options for C(swap) filesystems.
    type: str
  dump:
    description:
      - Dump (see fstab(5)).
      - Note that if set to C(null) and I(state) set to C(present),
        it will cease to work and duplicate entries will be made
        with subsequent runs.
      - Has no effect on Solaris systems.
    type: str
    default: 0
  passno:
    description:
      - Passno (see fstab(5)).
      - Note that if set to C(null) and I(state) set to C(present),
        it will cease to work and duplicate entries will be made
        with subsequent runs.
      - Deprecated on Solaris systems.
    type: str
    default: 0
  state:
    description:
      - If C(mounted), the device will be actively mounted and appropriately
        configured in I(fstab). If the mount point is not present, the mount
        point will be created (unless I(fstype=swap)).
      - If C(unmounted), the device will be unmounted without changing I(fstab).
      - C(present) only specifies that the device is to be configured in
        I(fstab) and does not trigger or require a mount.
      - C(absent) specifies that the device mount's entry will be removed from
        I(fstab) and will also unmount the device and remove the mount
        point.
      - C(remounted) specifies that the device will be remounted for when you
        want to force a refresh on the mount itself (added in 2.9). This will
        always return changed=true. If I(opts) is set, the options will be
        applied to the remount, but will not change I(fstab).  Additionally,
        if I(opts) is set, and the remount command fails, the module will
        error to prevent unexpected mount changes.  Try using C(mounted)
        instead to work around this issue.
    type: str
    required: true
    choices: [ absent, mounted, present, unmounted, remounted ]
  fstab:
    description:
      - File to use instead of C(/etc/fstab).
      - The filename must not start with a dot, and must end with C(.fstab),
        otherwise it is silently ignored. It is also ignored by mount helpers
        (for filesystems not natively supported by the C(mount) command).
      - You should not use this option unless you really know what you are doing.
      - This might be useful if you need to configure mountpoints in a chroot environment.
      - OpenBSD does not allow specifying alternate fstab files with mount so do not
        use this on OpenBSD with any state that operates on the live filesystem.
      - This parameter defaults to /etc/fstab or /etc/vfstab on Solaris.
    type: str
  boot:
    description:
      - Determines if the filesystem should be mounted on boot.
      - Only applies to Solaris systems. Defaults to C(true) unless I(fstype=swap).
    type: bool
    default: yes
  backup:
    description:
      - Create a backup file including the timestamp information so you can get
        the original file back if you somehow clobbered it incorrectly.
    type: bool
    default: no
notes:
  - As of Ansible 2.3, the I(name) option has been changed to I(path) as
    default, but I(name) still works as well.
  - Using C(remounted) with I(opts) set may create unexpected results based on
    the existing options already defined on mount, so care should be taken to
    ensure that conflicting options are not present before hand.
  - Support for swap spaces activation/deactivation as been added in version
    1.2.0 of C(ansible.posix).
  - Strictly speaking, swap filesystems can't be C(mounted), C(unmounted) or
    C(remounted). The module internally calls C(swapon) and C(swapoff) commands
    to enable or disable such filesystems and make them usable by the kernel.
'''

EXAMPLES = r'''
# Before 2.3, option 'name' was used instead of 'path'
- name: Mount DVD read-only
  ansible.posix.mount:
    path: /mnt/dvd
    src: /dev/sr0
    fstype: iso9660
    opts: ro,noauto
    state: present

- name: Mount up device by label
  ansible.posix.mount:
    path: /srv/disk
    src: LABEL=SOME_LABEL
    fstype: ext4
    state: present

- name: Mount up device by UUID
  ansible.posix.mount:
    path: /home
    src: UUID=b3e48f45-f933-4c8e-a700-22a159ec9077
    fstype: xfs
    opts: noatime
    state: present

- name: Unmount a mounted volume
  ansible.posix.mount:
    path: /tmp/mnt-pnt
    state: unmounted

- name: Remount a mounted volume
  ansible.posix.mount:
    path: /tmp/mnt-pnt
    state: remounted

# The following will not save changes to fstab, and only be temporary until
# a reboot, or until calling "state: unmounted" followed by "state: mounted"
# on the same "path"
- name: Remount a mounted volume and append exec to the existing options
  ansible.posix.mount:
    path: /tmp
    state: remounted
    opts: exec

- name: Mount and bind a volume
  ansible.posix.mount:
    path: /system/new_volume/boot
    src: /boot
    opts: bind
    state: mounted
    fstype: none

- name: Mount an NFS volume
  ansible.posix.mount:
    src: 192.168.1.100:/nfs/ssd/shared_data
    path: /mnt/shared_data
    opts: rw,sync,hard,intr
    state: mounted
    fstype: nfs

- name: Enable swap device with priority=1 (Linux)
  ansible.posix.mount:
    src: /dev/mapper/vg0-swap
    fstype: swap
    path: none
    opts: pri=1
    state: mounted

- name: Enable a swapfile (Linux, Solaris)
  ansible.posix.mount:
    src: /var/swapfile
    fstype: swap
    path: none
    state: mounted

- name: Enable a swapfile (FreeBSD)
  ansible.posix.mount:
    src: md99
    fstype: swap
    path: none
    opts: file=/var/swapfile
    state: mounted
'''


import errno
import os
import platform

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.ansible.posix.plugins.module_utils.mount import ismount
from ansible.module_utils.six import iteritems
from ansible.module_utils._text import to_bytes, to_native
from ansible.module_utils.parsing.convert_bool import boolean


SYSTEM = platform.system().lower()


def write_fstab(module, lines, path):
    if module.params['backup']:
        module.backup_local(path)

    fs_w = open(path, 'w')

    for l in lines:
        fs_w.write(l)

    fs_w.flush()
    fs_w.close()


def _escape_fstab(v):
    """Escape invalid characters in fstab fields.

    space (040)
    ampersand (046)
    backslash (134)
    """

    if isinstance(v, int):
        return v
    else:
        return(
            v.
            replace('\\', '\\134').
            replace(' ', '\\040').
            replace('&', '\\046'))


def set_mount(module, args):
    """Set/change a mount point location in fstab."""
    name, backup_lines, changed = _set_mount_save_old(module, args)
    return name, changed


def _set_mount_save_old(module, args):
    """Set/change a mount point location in fstab. Save the old fstab contents."""

    to_write = []
    old_lines = []
    exists = False
    changed = False
    escaped_args = dict([(k, _escape_fstab(v)) for k, v in iteritems(args)])
    new_line = '%(src)s %(name)s %(fstype)s %(opts)s %(dump)s %(passno)s\n'

    if SYSTEM == 'sunos':
        new_line = (
            '%(src)s - %(name)s %(fstype)s %(passno)s %(boot)s %(opts)s\n')

    for line in open(args['fstab'], 'r').readlines():
        old_lines.append(line)

        if not line.strip():
            to_write.append(line)

            continue

        if line.strip().startswith('#'):
            to_write.append(line)

            continue

        fields = line.split()

        # Check if we got a valid line for splitting
        # (on Linux the 5th and the 6th field is optional)
        if (
                SYSTEM == 'sunos' and len(fields) != 7 or
                SYSTEM == 'linux' and len(fields) not in [4, 5, 6] or
                SYSTEM not in ['sunos', 'linux'] and len(fields) != 6):
            to_write.append(line)

            continue

        ld = {}

        if SYSTEM == 'sunos':
            (
                ld['src'],
                dash,
                ld['name'],
                ld['fstype'],
                ld['passno'],
                ld['boot'],
                ld['opts']
            ) = fields
        else:
            fields_labels = ['src', 'name', 'fstype', 'opts', 'dump', 'passno']

            # The last two fields are optional on Linux so we fill in default values
            ld['dump'] = 0
            ld['passno'] = 0

            # Fill in the rest of the available fields
            for i, field in enumerate(fields):
                ld[fields_labels[i]] = field

        # Check if we found the correct line
        if (
                ld['name'] != escaped_args['name'] or (
                    # In the case of swap, check the src instead
                    ld['fstype'] == 'swap' and
                    ld['src'] != args['src'])):
            to_write.append(line)

            continue

        # If we got here we found a match - let's check if there is any
        # difference
        exists = True
        args_to_check = ('src', 'fstype', 'opts', 'dump', 'passno')

        if SYSTEM == 'sunos':
            args_to_check = ('src', 'fstype', 'passno', 'boot', 'opts')

        for t in args_to_check:
            if ld[t] != escaped_args[t]:
                ld[t] = escaped_args[t]
                changed = True

        if changed:
            to_write.append(new_line % ld)
        else:
            to_write.append(line)

    if not exists:
        to_write.append(new_line % escaped_args)
        changed = True

    if changed and not module.check_mode:
        write_fstab(module, to_write, args['fstab'])

    return (args['name'], old_lines, changed)


def unset_mount(module, args):
    """Remove a mount point from fstab."""

    to_write = []
    changed = False
    escaped_name = _escape_fstab(args['name'])

    for line in open(args['fstab'], 'r').readlines():
        if not line.strip():
            to_write.append(line)

            continue

        if line.strip().startswith('#'):
            to_write.append(line)

            continue

        # Check if we got a valid line for splitting
        if (
                SYSTEM == 'sunos' and len(line.split()) != 7 or
                SYSTEM != 'sunos' and len(line.split()) != 6):
            to_write.append(line)

            continue

        ld = {}

        if SYSTEM == 'sunos':
            (
                ld['src'],
                dash,
                ld['name'],
                ld['fstype'],
                ld['passno'],
                ld['boot'],
                ld['opts']
            ) = line.split()
        else:
            (
                ld['src'],
                ld['name'],
                ld['fstype'],
                ld['opts'],
                ld['dump'],
                ld['passno']
            ) = line.split()

        if (
                ld['name'] != escaped_name or (
                    # In the case of swap, check the src instead
                    ld['fstype'] == 'swap' and
                    ld['src'] != args['src'])):
            to_write.append(line)

            continue

        # If we got here we found a match - continue and mark changed
        changed = True

    if changed and not module.check_mode:
        write_fstab(module, to_write, args['fstab'])

    return (args['name'], changed)


def _set_fstab_args(fstab_file):
    result = []

    if (
            fstab_file and
            fstab_file != '/etc/fstab' and
            SYSTEM != 'sunos'):
        if SYSTEM.endswith('bsd'):
            result.append('-F')
        else:
            result.append('-T')

        result.append(fstab_file)

    return result


def mount(module, args):
    """Mount up a path or remount if needed."""

    mount_bin = module.get_bin_path('mount', required=True)
    name = args['name']
    cmd = [mount_bin]

    if SYSTEM == 'openbsd':
        # Use module.params['fstab'] here as args['fstab'] has been set to the
        # default value.
        if module.params['fstab'] is not None:
            module.fail_json(
                msg=(
                    'OpenBSD does not support alternate fstab files. Do not '
                    'specify the fstab parameter for OpenBSD hosts'))
    else:
        cmd += _set_fstab_args(args['fstab'])

    cmd += [name]

    rc, out, err = module.run_command(cmd)

    if rc == 0:
        return 0, ''
    else:
        return rc, out + err


def umount(module, path):
    """Unmount a path."""

    umount_bin = module.get_bin_path('umount', required=True)
    cmd = [umount_bin, path]

    rc, out, err = module.run_command(cmd)

    if rc == 0:
        return 0, ''
    else:
        return rc, out + err


def remount(module, args):
    """Try to use 'remount' first and fallback to (u)mount if unsupported."""
    mount_bin = module.get_bin_path('mount', required=True)
    cmd = [mount_bin]

    # Multiplatform remount opts
    if SYSTEM.endswith('bsd'):
        if module.params['state'] == 'remounted' and args['opts'] != 'defaults':
            cmd += ['-u', '-o', args['opts']]
        else:
            cmd += ['-u']
    else:
        if module.params['state'] == 'remounted' and args['opts'] != 'defaults':
            cmd += ['-o', 'remount,' + args['opts']]
        else:
            cmd += ['-o', 'remount']

    if SYSTEM == 'openbsd':
        # Use module.params['fstab'] here as args['fstab'] has been set to the
        # default value.
        if module.params['fstab'] is not None:
            module.fail_json(
                msg=(
                    'OpenBSD does not support alternate fstab files. Do not '
                    'specify the fstab parameter for OpenBSD hosts'))
    else:
        cmd += _set_fstab_args(args['fstab'])

    cmd += [args['name']]
    out = err = ''

    try:
        if SYSTEM.endswith('bsd'):
            # Note: Forcing BSDs to do umount/mount due to BSD remount not
            # working as expected (suspect bug in the BSD mount command)
            # Interested contributor could rework this to use mount options on
            # the CLI instead of relying on fstab
            # https://github.com/ansible/ansible-modules-core/issues/5591
            rc = 1
        else:
            rc, out, err = module.run_command(cmd)
    except Exception:
        rc = 1

    msg = ''

    if rc != 0:
        msg = out + err

        if module.params['state'] == 'remounted' and args['opts'] != 'defaults':
            module.fail_json(
                msg=(
                    'Options were specified with remounted, but the remount '
                    'command failed. Failing in order to prevent an '
                    'unexpected mount result. Try replacing this command with '
                    'a "state: unmounted" followed by a "state: mounted" '
                    'using the full desired mount options instead.'))

        rc, msg = umount(module, args['name'])

        if rc == 0:
            rc, msg = mount(module, args)

    return rc, msg


# Note if we wanted to put this into module_utils we'd have to get permission
# from @jupeter -- https://github.com/ansible/ansible-modules-core/pull/2923
# @jtyr -- https://github.com/ansible/ansible-modules-core/issues/4439
# and @abadger to relicense from GPLv3+
def is_bind_mounted(module, linux_mounts, dest, src=None, fstype=None):
    """Return whether the dest is bind mounted

    :arg module: The AnsibleModule (used for helper functions)
    :arg dest: The directory to be mounted under. This is the primary means
        of identifying whether the destination is mounted.
    :kwarg src: The source directory. If specified, this is used to help
        ensure that we are detecting that the correct source is mounted there.
    :kwarg fstype: The filesystem type. If specified this is also used to
        help ensure that we are detecting the right mount.
    :kwarg linux_mounts: Cached list of mounts for Linux.
    :returns: True if the dest is mounted with src otherwise False.
    """

    is_mounted = False

    if SYSTEM == 'linux' and linux_mounts is not None:
        if src is None:
            # That's for unmounted/absent
            if dest in linux_mounts:
                is_mounted = True
        else:
            if dest in linux_mounts:
                is_mounted = linux_mounts[dest]['src'] == src

    else:
        bin_path = module.get_bin_path('mount', required=True)
        cmd = '%s -l' % bin_path
        rc, out, err = module.run_command(cmd)
        mounts = []

        if len(out) > 0:
            mounts = to_native(out).strip().split('\n')

        for mnt in mounts:
            arguments = mnt.split()

            if (
                    (arguments[0] == src or src is None) and
                    arguments[2] == dest and
                    (arguments[4] == fstype or fstype is None)):
                is_mounted = True

            if is_mounted:
                break

    return is_mounted


def get_linux_mounts(module, mntinfo_file="/proc/self/mountinfo"):
    """Gather mount information"""

    try:
        f = open(mntinfo_file)
    except IOError:
        return

    lines = map(str.strip, f.readlines())

    try:
        f.close()
    except IOError:
        module.fail_json(msg="Cannot close file %s" % mntinfo_file)

    mntinfo = {}

    for line in lines:
        fields = line.split()

        record = {
            'id': int(fields[0]),
            'parent_id': int(fields[1]),
            'root': fields[3],
            'dst': fields[4],
            'opts': fields[5],
            'fs': fields[-3],
            'src': fields[-2]
        }

        mntinfo[record['id']] = record

    mounts = {}

    for mnt in mntinfo.values():
        if mnt['parent_id'] != 1 and mnt['parent_id'] in mntinfo:
            m = mntinfo[mnt['parent_id']]
            if (
                    len(m['root']) > 1 and
                    mnt['root'].startswith("%s/" % m['root'])):
                # Omit the parent's root in the child's root
                # == Example:
                # 140 136 253:2 /rootfs / rw - ext4 /dev/sdb2 rw
                # 141 140 253:2 /rootfs/tmp/aaa /tmp/bbb rw - ext4 /dev/sdb2 rw
                # == Expected result:
                # src=/tmp/aaa
                mnt['root'] = mnt['root'][len(m['root']):]

            # Prepend the parent's dst to the child's root
            # == Example:
            # 42 60 0:35 / /tmp rw - tmpfs tmpfs rw
            # 78 42 0:35 /aaa /tmp/bbb rw - tmpfs tmpfs rw
            # == Expected result:
            # src=/tmp/aaa
            if m['dst'] != '/':
                mnt['root'] = "%s%s" % (m['dst'], mnt['root'])
            src = mnt['root']
        else:
            src = mnt['src']

        record = {
            'dst': mnt['dst'],
            'src': src,
            'opts': mnt['opts'],
            'fs': mnt['fs']
        }

        mounts[mnt['dst']] = record

    return mounts


def is_swap(module, args):
    """Return True if the device/file is an active swap space, False otherwise."""

    if module.params['fstype'] != 'swap':
        return False

    if SYSTEM == 'sunos':
        swap_bin = module.get_bin_path('swap', required=True)
        cmd = [swap_bin, '-l']
    elif SYSTEM.endswith('bsd'):
        swapctl_bin = module.get_bin_path('swapctl', required=True)
        cmd = [swapctl_bin, '-l']
    else:
        # swapon is supposed to be the standard command
        swapon_bin = module.get_bin_path('swapon', required=True)
        cmd = [swapon_bin]

    rc, out, err = module.run_command(cmd)

    if rc:
        module.fail_json(msg="Error while querying active swaps: %s" % err)

    # Get the first field of each line but the header
    devices = [x.split()[0] for x in out.splitlines()[1:]]
    dev = os.path.realpath(args['src'])

    if SYSTEM == 'linux':
        if args['src'].startswith('UUID='):
            uuid_path = os.path.join('/dev/disk/by-uuid', args['src'].split('=')[1])
            dev = os.path.realpath(uuid_path)
        elif args['src'].startswith('LABEL='):
            label_path = os.path.join('/dev/disk/by-label', args['src'].split('=')[1])
            dev = os.path.realpath(label_path)
    elif SYSTEM == 'freebsd':
        if args['src'].startswith('md'):
            dev = os.path.join('/dev', args['src'])

    return bool(dev in devices)


def swapon(module, args):
    """Activate a swap device/file with the proper options."""

    if SYSTEM == 'sunos':
        swap_bin = module.get_bin_path('swap', required=True)
        cmd = [swap_bin, '-a']
    elif SYSTEM.endswith('bsd'):
        swapctl_bin = module.get_bin_path('swapctl', required=True)
        cmd = [swapctl_bin, '-a']
    else:
        # swapon is supposed to be the standard command, isn't it ?
        swapon_bin = module.get_bin_path('swapon', required=True)
        cmd = [swapon_bin]

    # Only 'swapon -a' applies options from fstab, otherwise they are ignored
    # unless provided on command line with '-o opts'. But not all versions of
    # swapon accept -o or --options. So we don't use it here, but at least we
    # keep the 'priority' and 'discard' flags available on Linux.
    if SYSTEM == 'linux':
        for opt in args['opts'].split(','):
            if opt.startswith('pri='):
                cmd += ['-p', opt.split('=')[1]]
            elif opt.startswith('discard'):
                cmd += ['--%s' % opt]

    if SYSTEM == 'freebsd' and args['src'].startswith('md'):
        cmd += [os.path.join('/dev', args['src'])]
    else:
        cmd += [args['src']]

    rc, out, err = module.run_command(cmd)

    if rc:
        return rc, out + err
    return 0, ''


def swapoff(module, args):
    """Deactivate a swap device/file."""

    if SYSTEM == 'sunos':
        swap_bin = module.get_bin_path('swap', required=True)
        cmd = [swap_bin, '-d']
    elif SYSTEM.endswith('bsd'):
        swapctl_bin = module.get_bin_path('swapctl', required=True)
        cmd = [swapctl_bin, '-d']
    else:
        # swapoff is supposed to be the standard command, isn't it ?
        swapoff_bin = module.get_bin_path('swapoff', required=True)
        cmd = [swapoff_bin]

    if SYSTEM == 'freebsd' and args['src'].startswith('md'):
        cmd += [os.path.join('/dev', args['src'])]
    else:
        cmd += [args['src']]

    rc, out, err = module.run_command(cmd)

    if rc:
        return rc, out + err
    return 0, ''


def reswap(module, args):
    """Deactivate a swap device/file and reactivate it with new options."""

    if is_swap(module, args):
        rc, msg = swapoff(module, args)
        if rc:
            return rc, msg

    rc, msg = swapon(module, args)
    if rc:
        return rc, msg
    return 0, ''


def main():
    module = AnsibleModule(
        argument_spec=dict(
            boot=dict(type='bool', default=True),
            dump=dict(type='str'),
            fstab=dict(type='str'),
            fstype=dict(type='str'),
            path=dict(type='path', required=True, aliases=['name']),
            opts=dict(type='str'),
            passno=dict(type='str', no_log=False),
            src=dict(type='path'),
            backup=dict(type='bool', default=False),
            state=dict(type='str', required=True,
                       choices=['absent', 'mounted', 'present', 'unmounted', 'remounted']),
        ),
        supports_check_mode=True,
        required_if=(
            ['state', 'mounted', ['src', 'fstype']],
            ['state', 'present', ['src', 'fstype']],
            ['fstype', 'swap', ['src']],
        ),
    )

    fstype = module.params['fstype']

    # swapon/swapoff (and the likes) don't honor alternative fstab locations
    # the same way the mount command does, that could make things very, very
    # complicated...
    if fstype == 'swap':
        if SYSTEM == 'sunos':
            swap_fstab_file = '/etc/vfstab'
            swap_mountpoint = '-'
        else:
            swap_fstab_file = '/etc/fstab'
            swap_mountpoint = 'none'

        if module.params['fstab'] not in (None, swap_fstab_file):
            module.fail_json(msg="option 'fstype=swap' does not support alternative fstab locations")
        if module.params['path'] != swap_mountpoint:
            module.fail_json(msg="swap filesystems can't be mounted, please set path to '%s'" %
                             swap_mountpoint)

    # solaris args:
    #   name, src, fstype, opts, boot, passno, state, fstab=/etc/vfstab
    # linux args:
    #   name, src, fstype, opts, dump, passno, state, fstab=/etc/fstab
    # Note: Do not modify module.params['fstab'] as we need to know if the user
    # explicitly specified it in mount() and remount()
    if SYSTEM == 'sunos':
        args = dict(
            name=module.params['path'],
            opts='-',
            passno='-',
            fstab=module.params['fstab'],
            boot='yes' if module.params['boot'] else 'no'
        )
        if args['fstab'] is None:
            args['fstab'] = '/etc/vfstab'

        # swap spaces are used internally by kernels and have no mountpoint
        if fstype == 'swap':
            args['boot'] = 'no'
    else:
        args = dict(
            name=module.params['path'],
            opts='defaults',
            dump='0',
            passno='0',
            fstab=module.params['fstab']
        )
        if args['fstab'] is None:
            args['fstab'] = '/etc/fstab'

        # Override default value of options field for swap filesystems
        if fstype == 'swap':
            args['opts'] = 'sw'
        # FreeBSD doesn't have any 'default' so set 'rw' instead
        elif SYSTEM == 'freebsd':
            args['opts'] = 'rw'

    linux_mounts = []

    # Cache all mounts here in order we have consistent results if we need to
    # call is_bind_mounted() multiple times
    if SYSTEM == 'linux':
        linux_mounts = get_linux_mounts(module)

        if linux_mounts is None:
            args['warnings'] = (
                'Cannot open file /proc/self/mountinfo. '
                'Bind mounts might be misinterpreted.')

    # Override defaults with user specified params
    for key in ('src', 'fstype', 'passno', 'opts', 'dump', 'fstab'):
        if module.params[key] is not None:
            args[key] = module.params[key]

    # If fstab file does not exist, we first need to create it. This mainly
    # happens when fstab option is passed to the module.
    if not os.path.exists(args['fstab']):
        if not os.path.exists(os.path.dirname(args['fstab'])):
            os.makedirs(os.path.dirname(args['fstab']))
        try:
            open(args['fstab'], 'a').close()
        except PermissionError as e:
            module.fail_json(msg="Failed to open %s due to permission issue" % args['fstab'])
        except Exception as e:
            module.fail_json(msg="Failed to open %s due to %s" % (args['fstab'], to_native(e)))

    # absent:
    #   Remove from fstab and unmounted.
    # unmounted:
    #   Do not change fstab state, but unmount.
    # present:
    #   Add to fstab, do not change mount state.
    # mounted:
    #   Add to fstab if not there and make sure it is mounted. If it has
    #   changed in fstab then remount it.

    state = module.params['state']
    name = args['name']
    changed = False

    if state == 'absent':
        name, changed = unset_mount(module, args)

        if changed and not module.check_mode:
            if ismount(name) or is_bind_mounted(module, linux_mounts, name):
                res, msg = umount(module, name)

                if res:
                    module.fail_json(
                        msg="Error unmounting %s: %s" % (name, msg))
            elif is_swap(module, args):
                res, msg = swapoff(module, args)

                if res:
                    module.fail_json(
                        msg="Error disabling swap space %s: %s" % (args['src'], msg))

            if os.path.exists(name):
                try:
                    os.rmdir(name)
                except (OSError, IOError) as e:
                    module.fail_json(msg="Error rmdir %s: %s" % (name, to_native(e)))
    elif state == 'unmounted':
        if ismount(name) or is_bind_mounted(module, linux_mounts, name):
            if not module.check_mode:
                res, msg = umount(module, name)

                if res:
                    module.fail_json(
                        msg="Error unmounting %s: %s" % (name, msg))

            changed = True
        elif is_swap(module, args):
            if not module.check_mode:
                res, msg = swapoff(module, args)

                if res:
                    module.fail_json(
                        msg="Error disabling swap space %s: %s" % (args['src'], msg))

            changed = True
    elif state == 'mounted':
        dirs_created = []
        if fstype != 'swap' and not os.path.exists(name) and not module.check_mode:
            try:
                # Something like mkdir -p but with the possibility to undo.
                # Based on some copy-paste from the "file" module.
                curpath = ''
                for dirname in name.strip('/').split('/'):
                    curpath = '/'.join([curpath, dirname])
                    # Remove leading slash if we're creating a relative path
                    if not os.path.isabs(name):
                        curpath = curpath.lstrip('/')

                    b_curpath = to_bytes(curpath, errors='surrogate_or_strict')
                    if not os.path.exists(b_curpath):
                        try:
                            os.mkdir(b_curpath)
                            dirs_created.append(b_curpath)
                        except OSError as ex:
                            # Possibly something else created the dir since the os.path.exists
                            # check above. As long as it's a dir, we don't need to error out.
                            if not (ex.errno == errno.EEXIST and os.path.isdir(b_curpath)):
                                raise

            except (OSError, IOError) as e:
                module.fail_json(
                    msg="Error making dir %s: %s" % (name, to_native(e)))

        name, backup_lines, changed = _set_mount_save_old(module, args)
        res = 0

        if (
                ismount(name) or
                is_bind_mounted(
                    module, linux_mounts, name, args['src'], args['fstype'])):
            if changed and not module.check_mode:
                res, msg = remount(module, args)
                changed = True
        elif is_swap(module, args):
            if changed and not module.check_mode:
                res, msg = reswap(module, args)
                changed = True
        else:
            changed = True

            if not module.check_mode:
                if fstype == 'swap':
                    res, msg = swapon(module, args)
                else:
                    res, msg = mount(module, args)

        if res:
            # Not restoring fstab after a failed mount was reported as a bug,
            # ansible/ansible#59183
            # A non-working fstab entry may break the system at the reboot,
            # so undo all the changes if possible.
            try:
                write_fstab(module, backup_lines, args['fstab'])
            except Exception:
                pass

            try:
                for dirname in dirs_created[::-1]:
                    os.rmdir(dirname)
            except Exception:
                pass

            if fstype == 'swap':
                error_msg = "Error enabling swap space %s: %s" % (args['src'], msg)
            else:
                error_msg = "Error mounting %s: %s" % (name, msg)

            module.fail_json(msg=error_msg)
    elif state == 'present':
        name, changed = set_mount(module, args)
    elif state == 'remounted':
        if not module.check_mode:
            if fstype == 'swap':
                res, msg = reswap(module, args)

                if res:
                    module.fail_json(msg="Error re-enabling swap space %s: %s" % (args['src'], msg))
            else:
                res, msg = remount(module, args)

                if res:
                    module.fail_json(msg="Error remounting %s: %s" % (name, msg))

        changed = True
    else:
        module.fail_json(msg='Unexpected position reached')

    # If the managed node is Solaris, convert the boot value type to Boolean
    #  to match the type of return value with the module argument.
    if platform.system().lower() == 'sunos':
        args['boot'] = boolean(args['boot'])
    module.exit_json(changed=changed, **args)


if __name__ == '__main__':
    main()
