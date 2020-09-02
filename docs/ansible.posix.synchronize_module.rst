.. _ansible.posix.synchronize_module:


*************************
ansible.posix.synchronize
*************************

**A wrapper around rsync to make common tasks in your playbooks quick and easy**


Version added: 1.0.0

.. contents::
   :local:
   :depth: 1


Synopsis
--------
- ``synchronize`` is a wrapper around rsync to make common tasks in your playbooks quick and easy.
- It is run and originates on the local host where Ansible is being run.
- Of course, you could just use the ``command`` action to call rsync yourself, but you also have to add a fair number of boilerplate options and host facts.
- This module is not intended to provide access to the full power of rsync, but does make the most common invocations easier to implement. You `still` may need to call rsync directly via ``command`` or ``shell`` depending on your use case.




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
                    <b>archive</b>
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
                        <div>Mirrors the rsync archive flag, enables recursive, links, perms, times, owner, group flags and -D.</div>
                </td>
            </tr>
            <tr>
                <td colspan="1">
                    <div class="ansibleOptionAnchor" id="parameter-"></div>
                    <b>checksum</b>
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
                        <div>Skip based on checksum, rather than mod-time &amp; size; Note that that &quot;archive&quot; option is still enabled by default - the &quot;checksum&quot; option will not disable it.</div>
                </td>
            </tr>
            <tr>
                <td colspan="1">
                    <div class="ansibleOptionAnchor" id="parameter-"></div>
                    <b>compress</b>
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
                        <div>Compress file data during the transfer.</div>
                        <div>In most cases, leave this enabled unless it causes problems.</div>
                </td>
            </tr>
            <tr>
                <td colspan="1">
                    <div class="ansibleOptionAnchor" id="parameter-"></div>
                    <b>copy_links</b>
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
                        <div>Copy symlinks as the item that they point to (the referent) is copied, rather than the symlink.</div>
                </td>
            </tr>
            <tr>
                <td colspan="1">
                    <div class="ansibleOptionAnchor" id="parameter-"></div>
                    <b>delete</b>
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
                        <div>Delete files in <code>dest</code> that don&#x27;t exist (after transfer, not before) in the <code>src</code> path.</div>
                        <div>This option requires <code>recursive=yes</code>.</div>
                        <div>This option ignores excluded files and behaves like the rsync opt --delete-excluded.</div>
                </td>
            </tr>
            <tr>
                <td colspan="1">
                    <div class="ansibleOptionAnchor" id="parameter-"></div>
                    <b>dest</b>
                    <a class="ansibleOptionLink" href="#parameter-" title="Permalink to this option"></a>
                    <div style="font-size: small">
                        <span style="color: purple">string</span>
                         / <span style="color: red">required</span>
                    </div>
                </td>
                <td>
                </td>
                <td>
                        <div>Path on the destination host that will be synchronized from the source.</div>
                        <div>The path can be absolute or relative.</div>
                </td>
            </tr>
            <tr>
                <td colspan="1">
                    <div class="ansibleOptionAnchor" id="parameter-"></div>
                    <b>dest_port</b>
                    <a class="ansibleOptionLink" href="#parameter-" title="Permalink to this option"></a>
                    <div style="font-size: small">
                        <span style="color: purple">integer</span>
                    </div>
                </td>
                <td>
                </td>
                <td>
                        <div>Port number for ssh on the destination host.</div>
                        <div>Prior to Ansible 2.0, the ansible_ssh_port inventory var took precedence over this value.</div>
                        <div>This parameter defaults to the value of <code>ansible_ssh_port</code> or <code>ansible_port</code>, the <code>remote_port</code> config setting or the value from ssh client configuration if none of the former have been set.</div>
                </td>
            </tr>
            <tr>
                <td colspan="1">
                    <div class="ansibleOptionAnchor" id="parameter-"></div>
                    <b>dirs</b>
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
                        <div>Transfer directories without recursing.</div>
                </td>
            </tr>
            <tr>
                <td colspan="1">
                    <div class="ansibleOptionAnchor" id="parameter-"></div>
                    <b>existing_only</b>
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
                        <div>Skip creating new files on receiver.</div>
                </td>
            </tr>
            <tr>
                <td colspan="1">
                    <div class="ansibleOptionAnchor" id="parameter-"></div>
                    <b>group</b>
                    <a class="ansibleOptionLink" href="#parameter-" title="Permalink to this option"></a>
                    <div style="font-size: small">
                        <span style="color: purple">boolean</span>
                    </div>
                </td>
                <td>
                        <ul style="margin: 0; padding: 0"><b>Choices:</b>
                                    <li>no</li>
                                    <li>yes</li>
                        </ul>
                </td>
                <td>
                        <div>Preserve group.</div>
                        <div>This parameter defaults to the value of the archive option.</div>
                </td>
            </tr>
            <tr>
                <td colspan="1">
                    <div class="ansibleOptionAnchor" id="parameter-"></div>
                    <b>link_dest</b>
                    <a class="ansibleOptionLink" href="#parameter-" title="Permalink to this option"></a>
                    <div style="font-size: small">
                        <span style="color: purple">list</span>
                    </div>
                </td>
                <td>
                        <b>Default:</b><br/><div style="color: blue">null</div>
                </td>
                <td>
                        <div>Add a destination to hard link against during the rsync.</div>
                </td>
            </tr>
            <tr>
                <td colspan="1">
                    <div class="ansibleOptionAnchor" id="parameter-"></div>
                    <b>links</b>
                    <a class="ansibleOptionLink" href="#parameter-" title="Permalink to this option"></a>
                    <div style="font-size: small">
                        <span style="color: purple">boolean</span>
                    </div>
                </td>
                <td>
                        <ul style="margin: 0; padding: 0"><b>Choices:</b>
                                    <li>no</li>
                                    <li>yes</li>
                        </ul>
                </td>
                <td>
                        <div>Copy symlinks as symlinks.</div>
                        <div>This parameter defaults to the value of the archive option.</div>
                </td>
            </tr>
            <tr>
                <td colspan="1">
                    <div class="ansibleOptionAnchor" id="parameter-"></div>
                    <b>mode</b>
                    <a class="ansibleOptionLink" href="#parameter-" title="Permalink to this option"></a>
                    <div style="font-size: small">
                        <span style="color: purple">string</span>
                    </div>
                </td>
                <td>
                        <ul style="margin: 0; padding: 0"><b>Choices:</b>
                                    <li>pull</li>
                                    <li><div style="color: blue"><b>push</b>&nbsp;&larr;</div></li>
                        </ul>
                </td>
                <td>
                        <div>Specify the direction of the synchronization.</div>
                        <div>In push mode the localhost or delegate is the source.</div>
                        <div>In pull mode the remote host in context is the source.</div>
                </td>
            </tr>
            <tr>
                <td colspan="1">
                    <div class="ansibleOptionAnchor" id="parameter-"></div>
                    <b>owner</b>
                    <a class="ansibleOptionLink" href="#parameter-" title="Permalink to this option"></a>
                    <div style="font-size: small">
                        <span style="color: purple">boolean</span>
                    </div>
                </td>
                <td>
                        <ul style="margin: 0; padding: 0"><b>Choices:</b>
                                    <li>no</li>
                                    <li>yes</li>
                        </ul>
                </td>
                <td>
                        <div>Preserve owner (super user only).</div>
                        <div>This parameter defaults to the value of the archive option.</div>
                </td>
            </tr>
            <tr>
                <td colspan="1">
                    <div class="ansibleOptionAnchor" id="parameter-"></div>
                    <b>partial</b>
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
                        <div>Tells rsync to keep the partial file which should make a subsequent transfer of the rest of the file much faster.</div>
                </td>
            </tr>
            <tr>
                <td colspan="1">
                    <div class="ansibleOptionAnchor" id="parameter-"></div>
                    <b>perms</b>
                    <a class="ansibleOptionLink" href="#parameter-" title="Permalink to this option"></a>
                    <div style="font-size: small">
                        <span style="color: purple">boolean</span>
                    </div>
                </td>
                <td>
                        <ul style="margin: 0; padding: 0"><b>Choices:</b>
                                    <li>no</li>
                                    <li>yes</li>
                        </ul>
                </td>
                <td>
                        <div>Preserve permissions.</div>
                        <div>This parameter defaults to the value of the archive option.</div>
                </td>
            </tr>
            <tr>
                <td colspan="1">
                    <div class="ansibleOptionAnchor" id="parameter-"></div>
                    <b>private_key</b>
                    <a class="ansibleOptionLink" href="#parameter-" title="Permalink to this option"></a>
                    <div style="font-size: small">
                        <span style="color: purple">path</span>
                    </div>
                </td>
                <td>
                </td>
                <td>
                        <div>Specify the private key to use for SSH-based rsync connections (e.g. <code>~/.ssh/id_rsa</code>).</div>
                </td>
            </tr>
            <tr>
                <td colspan="1">
                    <div class="ansibleOptionAnchor" id="parameter-"></div>
                    <b>recursive</b>
                    <a class="ansibleOptionLink" href="#parameter-" title="Permalink to this option"></a>
                    <div style="font-size: small">
                        <span style="color: purple">boolean</span>
                    </div>
                </td>
                <td>
                        <ul style="margin: 0; padding: 0"><b>Choices:</b>
                                    <li>no</li>
                                    <li>yes</li>
                        </ul>
                </td>
                <td>
                        <div>Recurse into directories.</div>
                        <div>This parameter defaults to the value of the archive option.</div>
                </td>
            </tr>
            <tr>
                <td colspan="1">
                    <div class="ansibleOptionAnchor" id="parameter-"></div>
                    <b>rsync_opts</b>
                    <a class="ansibleOptionLink" href="#parameter-" title="Permalink to this option"></a>
                    <div style="font-size: small">
                        <span style="color: purple">list</span>
                    </div>
                </td>
                <td>
                        <b>Default:</b><br/><div style="color: blue">null</div>
                </td>
                <td>
                        <div>Specify additional rsync options by passing in an array.</div>
                        <div>Note that an empty string in <code>rsync_opts</code> will end up transfer the current working directory.</div>
                </td>
            </tr>
            <tr>
                <td colspan="1">
                    <div class="ansibleOptionAnchor" id="parameter-"></div>
                    <b>rsync_path</b>
                    <a class="ansibleOptionLink" href="#parameter-" title="Permalink to this option"></a>
                    <div style="font-size: small">
                        <span style="color: purple">string</span>
                    </div>
                </td>
                <td>
                </td>
                <td>
                        <div>Specify the rsync command to run on the remote host. See <code>--rsync-path</code> on the rsync man page.</div>
                        <div>To specify the rsync command to run on the local host, you need to set this your task var <code>ansible_rsync_path</code>.</div>
                </td>
            </tr>
            <tr>
                <td colspan="1">
                    <div class="ansibleOptionAnchor" id="parameter-"></div>
                    <b>rsync_timeout</b>
                    <a class="ansibleOptionLink" href="#parameter-" title="Permalink to this option"></a>
                    <div style="font-size: small">
                        <span style="color: purple">integer</span>
                    </div>
                </td>
                <td>
                        <b>Default:</b><br/><div style="color: blue">0</div>
                </td>
                <td>
                        <div>Specify a <code>--timeout</code> for the rsync command in seconds.</div>
                </td>
            </tr>
            <tr>
                <td colspan="1">
                    <div class="ansibleOptionAnchor" id="parameter-"></div>
                    <b>set_remote_user</b>
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
                        <div>Put user@ for the remote paths.</div>
                        <div>If you have a custom ssh config to define the remote user for a host that does not match the inventory user, you should set this parameter to <code>no</code>.</div>
                </td>
            </tr>
            <tr>
                <td colspan="1">
                    <div class="ansibleOptionAnchor" id="parameter-"></div>
                    <b>src</b>
                    <a class="ansibleOptionLink" href="#parameter-" title="Permalink to this option"></a>
                    <div style="font-size: small">
                        <span style="color: purple">string</span>
                         / <span style="color: red">required</span>
                    </div>
                </td>
                <td>
                </td>
                <td>
                        <div>Path on the source host that will be synchronized to the destination.</div>
                        <div>The path can be absolute or relative.</div>
                </td>
            </tr>
            <tr>
                <td colspan="1">
                    <div class="ansibleOptionAnchor" id="parameter-"></div>
                    <b>times</b>
                    <a class="ansibleOptionLink" href="#parameter-" title="Permalink to this option"></a>
                    <div style="font-size: small">
                        <span style="color: purple">boolean</span>
                    </div>
                </td>
                <td>
                        <ul style="margin: 0; padding: 0"><b>Choices:</b>
                                    <li>no</li>
                                    <li>yes</li>
                        </ul>
                </td>
                <td>
                        <div>Preserve modification times.</div>
                        <div>This parameter defaults to the value of the archive option.</div>
                </td>
            </tr>
            <tr>
                <td colspan="1">
                    <div class="ansibleOptionAnchor" id="parameter-"></div>
                    <b>use_ssh_args</b>
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
                        <div>Use the ssh_args specified in ansible.cfg.</div>
                </td>
            </tr>
            <tr>
                <td colspan="1">
                    <div class="ansibleOptionAnchor" id="parameter-"></div>
                    <b>verify_host</b>
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
                        <div>Verify destination host key.</div>
                </td>
            </tr>
    </table>
    <br/>


Notes
-----

.. note::
   - rsync must be installed on both the local and remote host.
   - For the ``synchronize`` module, the "local host" is the host `the synchronize task originates on`, and the "destination host" is the host `synchronize is connecting to`.
   - The "local host" can be changed to a different host by using `delegate_to`.  This enables copying between two remote hosts or entirely on one remote machine.
   - The user and permissions for the synchronize `src` are those of the user running the Ansible task on the local host (or the remote_user for a delegate_to host when delegate_to is used).

   - The user and permissions for the synchronize `dest` are those of the `remote_user` on the destination host or the `become_user` if `become=yes` is active.
   - In Ansible 2.0 a bug in the synchronize module made become occur on the "local host".  This was fixed in Ansible 2.0.1.
   - Currently, synchronize is limited to elevating permissions via passwordless sudo.  This is because rsync itself is connecting to the remote machine and rsync doesn't give us a way to pass sudo credentials in.
   - Currently there are only a few connection types which support synchronize (ssh, paramiko, local, and docker) because a sync strategy has been determined for those connection types.  Note that the connection for these must not need a password as rsync itself is making the connection and rsync does not provide us a way to pass a password to the connection.
   - Expect that dest=~/x will be ~<remote_user>/x even if using sudo.
   - Inspect the verbose output to validate the destination user/host/path are what was expected.
   - To exclude files and directories from being synchronized, you may add ``.rsync-filter`` files to the source directory.
   - rsync daemon must be up and running with correct permission when using rsync protocol in source or destination path.
   - The ``synchronize`` module forces `--delay-updates` to avoid leaving a destination in a broken in-between state if the underlying rsync process encounters an error. Those synchronizing large numbers of files that are willing to trade safety for performance should call rsync directly.
   - link_destination is subject to the same limitations as the underlying rsync daemon. Hard links are only preserved if the relative subtrees of the source and destination are the same. Attempts to hardlink into a directory that is a subdirectory of the source will be prevented.


See Also
--------

.. seealso::

   :ref:`copy_module`
      The official documentation on the **copy** module.
   :ref:`community.windows.win_robocopy_module`
      The official documentation on the **community.windows.win_robocopy** module.


Examples
--------

.. code-block:: yaml+jinja

    - name: Synchronization of src on the control machine to dest on the remote hosts
      ansible.posix.synchronize:
        src: some/relative/path
        dest: /some/absolute/path

    - name: Synchronization using rsync protocol (push)
      ansible.posix.synchronize:
        src: some/relative/path/
        dest: rsync://somehost.com/path/

    - name: Synchronization using rsync protocol (pull)
      ansible.posix.synchronize:
        mode: pull
        src: rsync://somehost.com/path/
        dest: /some/absolute/path/

    - name:  Synchronization using rsync protocol on delegate host (push)
      ansible.posix.synchronize:
        src: /some/absolute/path/
        dest: rsync://somehost.com/path/
      delegate_to: delegate.host

    - name: Synchronization using rsync protocol on delegate host (pull)
      ansible.posix.synchronize:
        mode: pull
        src: rsync://somehost.com/path/
        dest: /some/absolute/path/
      delegate_to: delegate.host

    - name: Synchronization without any --archive options enabled
      ansible.posix.synchronize:
        src: some/relative/path
        dest: /some/absolute/path
        archive: no

    - name: Synchronization with --archive options enabled except for --recursive
      ansible.posix.synchronize:
        src: some/relative/path
        dest: /some/absolute/path
        recursive: no

    - name: Synchronization with --archive options enabled except for --times, with --checksum option enabled
      ansible.posix.synchronize:
        src: some/relative/path
        dest: /some/absolute/path
        checksum: yes
        times: no

    - name: Synchronization without --archive options enabled except use --links
      ansible.posix.synchronize:
        src: some/relative/path
        dest: /some/absolute/path
        archive: no
        links: yes

    - name: Synchronization of two paths both on the control machine
      ansible.posix.synchronize:
        src: some/relative/path
        dest: /some/absolute/path
      delegate_to: localhost

    - name: Synchronization of src on the inventory host to the dest on the localhost in pull mode
      ansible.posix.synchronize:
        mode: pull
        src: some/relative/path
        dest: /some/absolute/path

    - name: Synchronization of src on delegate host to dest on the current inventory host.
      ansible.posix.synchronize:
        src: /first/absolute/path
        dest: /second/absolute/path
      delegate_to: delegate.host

    - name: Synchronize two directories on one remote host.
      ansible.posix.synchronize:
        src: /first/absolute/path
        dest: /second/absolute/path
      delegate_to: "{{ inventory_hostname }}"

    - name: Synchronize and delete files in dest on the remote host that are not found in src of localhost.
      ansible.posix.synchronize:
        src: some/relative/path
        dest: /some/absolute/path
        delete: yes
        recursive: yes

    # This specific command is granted su privileges on the destination
    - name: Synchronize using an alternate rsync command
      ansible.posix.synchronize:
        src: some/relative/path
        dest: /some/absolute/path
        rsync_path: su -c rsync

    # Example .rsync-filter file in the source directory
    # - var       # exclude any path whose last part is 'var'
    # - /var      # exclude any path starting with 'var' starting at the source directory
    # + /var/conf # include /var/conf even though it was previously excluded

    - name: Synchronize passing in extra rsync options
      ansible.posix.synchronize:
        src: /tmp/helloworld
        dest: /var/www/helloworld
        rsync_opts:
          - "--no-motd"
          - "--exclude=.git"

    # Hardlink files if they didn't change
    - name: Use hardlinks when synchronizing filesystems
      ansible.posix.synchronize:
        src: /tmp/path_a/foo.txt
        dest: /tmp/path_b/foo.txt
        link_dest: /tmp/path_a/

    # Specify the rsync binary to use on remote host and on local host
    - hosts: groupofhosts
      vars:
            ansible_rsync_path: /usr/gnu/bin/rsync

      tasks:
        - name: copy /tmp/localpath/ to remote location /tmp/remotepath
          ansible.posix.synchronize:
            src: /tmp/localpath/
            dest: /tmp/remotepath
            rsync_path: /usr/gnu/bin/rsync




Status
------


Authors
~~~~~~~

- Timothy Appnel (@tima)
