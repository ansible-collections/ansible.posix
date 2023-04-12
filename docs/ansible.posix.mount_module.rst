.. _ansible.posix.mount_module:


*******************
ansible.posix.mount
*******************

**Control active and configured mount points**


Version added: 1.0.0

.. contents::
   :local:
   :depth: 1


Synopsis
--------
- This module controls active and configured mount points in ``/etc/fstab``.




Parameters
----------

.. raw:: html

    <table  border=0 cellpadding=0 class="documentation-table">
        <tr>
            <th colspan="1">Parameter</th>
            <th>Choices/<font color="blue">Defaults</font></th>
            <th width="100%">Comments</th>
        </tr>
            <tr>
                <td colspan="1">
                    <div class="ansibleOptionAnchor" id="parameter-"></div>
                    <b>backup</b>
                    <a class="ansibleOptionLink" href="#parameter-" title="Permalink to this option"></a>
                    <div style="font-size: small">
                        <span style="color: purple">boolean</span>
                    </div>
                </td>
                <td>
                        <ul style="margin: 0; padding: 0"><b>Choices:</b>
                                    <li><div style="color: blue"><b>no</b>&nbsp;&larr;</div></li>
                                    <li>yes</li>
                        </ul>
                </td>
                <td>
                        <div>Create a backup file including the timestamp information so you can get the original file back if you somehow clobbered it incorrectly.</div>
                </td>
            </tr>
            <tr>
                <td colspan="1">
                    <div class="ansibleOptionAnchor" id="parameter-"></div>
                    <b>boot</b>
                    <a class="ansibleOptionLink" href="#parameter-" title="Permalink to this option"></a>
                    <div style="font-size: small">
                        <span style="color: purple">boolean</span>
                    </div>
                </td>
                <td>
                        <ul style="margin: 0; padding: 0"><b>Choices:</b>
                                    <li>no</li>
                                    <li><div style="color: blue"><b>yes</b>&nbsp;&larr;</div></li>
                        </ul>
                </td>
                <td>
                        <div>Determines if the filesystem should be mounted on boot.</div>
                        <div>Only applies to Solaris and Linux systems.</div>
                        <div>For Solaris systems, <code>true</code> will set <code>yes</code> as the value of mount at boot in <em>/etc/vfstab</em>.</div>
                        <div>For Linux, FreeBSD, NetBSD and OpenBSD systems, <code>false</code> will add <code>noauto</code> to mount options in <em>/etc/fstab</em>.</div>
                        <div>To avoid mount option conflicts, if <code>noauto</code> specified in <code>opts</code>, mount module will ignore <code>boot</code>.</div>
                        <div>This parameter is ignored when <em>state</em> is set to <code>ephemeral</code>.</div>
                </td>
            </tr>
            <tr>
                <td colspan="1">
                    <div class="ansibleOptionAnchor" id="parameter-"></div>
                    <b>dump</b>
                    <a class="ansibleOptionLink" href="#parameter-" title="Permalink to this option"></a>
                    <div style="font-size: small">
                        <span style="color: purple">string</span>
                    </div>
                </td>
                <td>
                        <b>Default:</b><br/><div style="color: blue">"0"</div>
                </td>
                <td>
                        <div>Dump (see fstab(5)).</div>
                        <div>Note that if set to <code>null</code> and <em>state</em> set to <code>present</code>, it will cease to work and duplicate entries will be made with subsequent runs.</div>
                        <div>Has no effect on Solaris systems or when used with <code>ephemeral</code>.</div>
                </td>
            </tr>
            <tr>
                <td colspan="1">
                    <div class="ansibleOptionAnchor" id="parameter-"></div>
                    <b>fstab</b>
                    <a class="ansibleOptionLink" href="#parameter-" title="Permalink to this option"></a>
                    <div style="font-size: small">
                        <span style="color: purple">string</span>
                    </div>
                </td>
                <td>
                </td>
                <td>
                        <div>File to use instead of <code>/etc/fstab</code>.</div>
                        <div>You should not use this option unless you really know what you are doing.</div>
                        <div>This might be useful if you need to configure mountpoints in a chroot environment.</div>
                        <div>OpenBSD does not allow specifying alternate fstab files with mount so do not use this on OpenBSD with any state that operates on the live filesystem.</div>
                        <div>This parameter defaults to /etc/fstab or /etc/vfstab on Solaris.</div>
                        <div>This parameter is ignored when <em>state</em> is set to <code>ephemeral</code>.</div>
                </td>
            </tr>
            <tr>
                <td colspan="1">
                    <div class="ansibleOptionAnchor" id="parameter-"></div>
                    <b>fstype</b>
                    <a class="ansibleOptionLink" href="#parameter-" title="Permalink to this option"></a>
                    <div style="font-size: small">
                        <span style="color: purple">string</span>
                    </div>
                </td>
                <td>
                </td>
                <td>
                        <div>Filesystem type.</div>
                        <div>Required when <em>state</em> is <code>present</code>, <code>mounted</code> or <code>ephemeral</code>.</div>
                </td>
            </tr>
            <tr>
                <td colspan="1">
                    <div class="ansibleOptionAnchor" id="parameter-"></div>
                    <b>opts</b>
                    <a class="ansibleOptionLink" href="#parameter-" title="Permalink to this option"></a>
                    <div style="font-size: small">
                        <span style="color: purple">string</span>
                    </div>
                </td>
                <td>
                </td>
                <td>
                        <div>Mount options (see fstab(5), or vfstab(4) on Solaris).</div>
                </td>
            </tr>
            <tr>
                <td colspan="1">
                    <div class="ansibleOptionAnchor" id="parameter-"></div>
                    <b>passno</b>
                    <a class="ansibleOptionLink" href="#parameter-" title="Permalink to this option"></a>
                    <div style="font-size: small">
                        <span style="color: purple">string</span>
                    </div>
                </td>
                <td>
                        <b>Default:</b><br/><div style="color: blue">"0"</div>
                </td>
                <td>
                        <div>Passno (see fstab(5)).</div>
                        <div>Note that if set to <code>null</code> and <em>state</em> set to <code>present</code>, it will cease to work and duplicate entries will be made with subsequent runs.</div>
                        <div>Deprecated on Solaris systems. Has no effect when used with <code>ephemeral</code>.</div>
                </td>
            </tr>
            <tr>
                <td colspan="1">
                    <div class="ansibleOptionAnchor" id="parameter-"></div>
                    <b>path</b>
                    <a class="ansibleOptionLink" href="#parameter-" title="Permalink to this option"></a>
                    <div style="font-size: small">
                        <span style="color: purple">path</span>
                         / <span style="color: red">required</span>
                    </div>
                </td>
                <td>
                </td>
                <td>
                        <div>Path to the mount point (e.g. <code>/mnt/files</code>).</div>
                        <div>Before Ansible 2.3 this option was only usable as <em>dest</em>, <em>destfile</em> and <em>name</em>.</div>
                        <div style="font-size: small; color: darkgreen"><br/>aliases: name</div>
                </td>
            </tr>
            <tr>
                <td colspan="1">
                    <div class="ansibleOptionAnchor" id="parameter-"></div>
                    <b>src</b>
                    <a class="ansibleOptionLink" href="#parameter-" title="Permalink to this option"></a>
                    <div style="font-size: small">
                        <span style="color: purple">path</span>
                    </div>
                </td>
                <td>
                </td>
                <td>
                        <div>Device (or NFS volume, or something else) to be mounted on <em>path</em>.</div>
                        <div>Required when <em>state</em> set to <code>present</code>, <code>mounted</code> or <code>ephemeral</code>.</div>
                </td>
            </tr>
            <tr>
                <td colspan="1">
                    <div class="ansibleOptionAnchor" id="parameter-"></div>
                    <b>state</b>
                    <a class="ansibleOptionLink" href="#parameter-" title="Permalink to this option"></a>
                    <div style="font-size: small">
                        <span style="color: purple">string</span>
                         / <span style="color: red">required</span>
                    </div>
                </td>
                <td>
                        <ul style="margin: 0; padding: 0"><b>Choices:</b>
                                    <li>absent</li>
                                    <li>absent_from_fstab</li>
                                    <li>mounted</li>
                                    <li>present</li>
                                    <li>unmounted</li>
                                    <li>remounted</li>
                                    <li>ephemeral</li>
                        </ul>
                </td>
                <td>
                        <div>If <code>mounted</code>, the device will be actively mounted and appropriately configured in <em>fstab</em>. If the mount point is not present, the mount point will be created.</div>
                        <div>If <code>unmounted</code>, the device will be unmounted without changing <em>fstab</em>.</div>
                        <div><code>present</code> only specifies that the device is to be configured in <em>fstab</em> and does not trigger or require a mount.</div>
                        <div><code>ephemeral</code> only specifies that the device is to be mounted, without changing <em>fstab</em>. If it is already mounted, a remount will be triggered. This will always return changed=True. If the mount point <em>path</em> has already a device mounted on, and its source is different than <em>src</em>, the module will fail to avoid unexpected unmount or mount point override. If the mount point is not present, the mount point will be created. The <em>fstab</em> is completely ignored. This option is added in version 1.5.0.</div>
                        <div><code>absent</code> specifies that the device mount&#x27;s entry will be removed from <em>fstab</em> and will also unmount the device and remove the mount point.</div>
                        <div><code>remounted</code> specifies that the device will be remounted for when you want to force a refresh on the mount itself (added in 2.9). This will always return changed=true. If <em>opts</em> is set, the options will be applied to the remount, but will not change <em>fstab</em>.  Additionally, if <em>opts</em> is set, and the remount command fails, the module will error to prevent unexpected mount changes.  Try using <code>mounted</code> instead to work around this issue.  <code>remounted</code> expects the mount point to be present in the <em>fstab</em>. To remount a mount point not registered in <em>fstab</em>, use <code>ephemeral</code> instead, especially with BSD nodes.</div>
                        <div><code>absent_from_fstab</code> specifies that the device mount&#x27;s entry will be removed from <em>fstab</em>. This option does not unmount it or delete the mountpoint.</div>
                </td>
            </tr>
    </table>
    <br/>


Notes
-----

.. note::
   - As of Ansible 2.3, the *name* option has been changed to *path* as default, but *name* still works as well.
   - Using ``remounted`` with *opts* set may create unexpected results based on the existing options already defined on mount, so care should be taken to ensure that conflicting options are not present before hand.



Examples
--------

.. code-block:: yaml

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
        opts: rw,sync,hard
        state: mounted
        fstype: nfs

    - name: Mount NFS volumes with noauto according to boot option
      ansible.posix.mount:
        src: 192.168.1.100:/nfs/ssd/shared_data
        path: /mnt/shared_data
        opts: rw,sync,hard
        boot: false
        state: mounted
        fstype: nfs

    - name: Mount ephemeral SMB volume
      ansible.posix.mount:
        src: //192.168.1.200/share
        path: /mnt/smb_share
        opts: "rw,vers=3,file_mode=0600,dir_mode=0700,dom={{ ad_domain }},username={{ ad_username }},password={{ ad_password }}"
        fstype: cifs
        state: ephemeral




Status
------


Authors
~~~~~~~

- Ansible Core Team
- Seth Vidal (@skvidal)
