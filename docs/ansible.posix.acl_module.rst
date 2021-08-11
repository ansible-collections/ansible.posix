.. _ansible.posix.acl_module:


*****************
ansible.posix.acl
*****************

**Set and retrieve file ACL information.**


Version added: 1.0.0

.. contents::
   :local:
   :depth: 1


Synopsis
--------
- Set and retrieve file ACL information.




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
                    <b>default</b>
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
                        <div>If the target is a directory, setting this to <code>yes</code> will make it the default ACL for entities created inside the directory.</div>
                        <div>Setting <code>default</code> to <code>yes</code> causes an error if the path is a file.</div>
                </td>
            </tr>
            <tr>
                <td colspan="1">
                    <div class="ansibleOptionAnchor" id="parameter-"></div>
                    <b>entity</b>
                    <a class="ansibleOptionLink" href="#parameter-" title="Permalink to this option"></a>
                    <div style="font-size: small">
                        <span style="color: purple">string</span>
                    </div>
                </td>
                <td>
                </td>
                <td>
                        <div>The actual user or group that the ACL applies to when matching entity types user or group are selected.</div>
                </td>
            </tr>
            <tr>
                <td colspan="1">
                    <div class="ansibleOptionAnchor" id="parameter-"></div>
                    <b>entry</b>
                    <a class="ansibleOptionLink" href="#parameter-" title="Permalink to this option"></a>
                    <div style="font-size: small">
                        <span style="color: purple">string</span>
                    </div>
                </td>
                <td>
                </td>
                <td>
                        <div>DEPRECATED.</div>
                        <div>The ACL to set or remove.</div>
                        <div>This must always be quoted in the form of <code>&lt;etype&gt;:&lt;qualifier&gt;:&lt;perms&gt;</code>.</div>
                        <div>The qualifier may be empty for some types, but the type and perms are always required.</div>
                        <div><code>-</code> can be used as placeholder when you do not care about permissions.</div>
                        <div>This is now superseded by entity, type and permissions fields.</div>
                </td>
            </tr>
            <tr>
                <td colspan="1">
                    <div class="ansibleOptionAnchor" id="parameter-"></div>
                    <b>etype</b>
                    <a class="ansibleOptionLink" href="#parameter-" title="Permalink to this option"></a>
                    <div style="font-size: small">
                        <span style="color: purple">string</span>
                    </div>
                </td>
                <td>
                        <ul style="margin: 0; padding: 0"><b>Choices:</b>
                                    <li>group</li>
                                    <li>mask</li>
                                    <li>other</li>
                                    <li>user</li>
                        </ul>
                </td>
                <td>
                        <div>The entity type of the ACL to apply, see <code>setfacl</code> documentation for more info.</div>
                </td>
            </tr>
            <tr>
                <td colspan="1">
                    <div class="ansibleOptionAnchor" id="parameter-"></div>
                    <b>follow</b>
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
                        <div>Whether to follow symlinks on the path if a symlink is encountered.</div>
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
                        <div>The full path of the file or object.</div>
                        <div style="font-size: small; color: darkgreen"><br/>aliases: name</div>
                </td>
            </tr>
            <tr>
                <td colspan="1">
                    <div class="ansibleOptionAnchor" id="parameter-"></div>
                    <b>permissions</b>
                    <a class="ansibleOptionLink" href="#parameter-" title="Permalink to this option"></a>
                    <div style="font-size: small">
                        <span style="color: purple">string</span>
                    </div>
                </td>
                <td>
                </td>
                <td>
                        <div>The permissions to apply/remove can be any combination of <code>r</code>, <code>w</code>, <code>x</code></div>
                        <div>(read, write and execute respectively), and <code>X</code> (execute permission if the file is a directory or already has execute permission for some user)</div>
                </td>
            </tr>
            <tr>
                <td colspan="1">
                    <div class="ansibleOptionAnchor" id="parameter-"></div>
                    <b>recalculate_mask</b>
                    <a class="ansibleOptionLink" href="#parameter-" title="Permalink to this option"></a>
                    <div style="font-size: small">
                        <span style="color: purple">string</span>
                    </div>
                </td>
                <td>
                        <ul style="margin: 0; padding: 0"><b>Choices:</b>
                                    <li><div style="color: blue"><b>default</b>&nbsp;&larr;</div></li>
                                    <li>mask</li>
                                    <li>no_mask</li>
                        </ul>
                </td>
                <td>
                        <div>Select if and when to recalculate the effective right masks of the files.</div>
                        <div>See <code>setfacl</code> documentation for more info.</div>
                        <div>Incompatible with <code>state=query</code>.</div>
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
                                    <li><div style="color: blue"><b>no</b>&nbsp;&larr;</div></li>
                                    <li>yes</li>
                        </ul>
                </td>
                <td>
                        <div>Recursively sets the specified ACL.</div>
                        <div>Incompatible with <code>state=query</code>.</div>
                        <div>Alias <code>recurse</code> added in version 1.3.0.</div>
                        <div style="font-size: small; color: darkgreen"><br/>aliases: recurse</div>
                </td>
            </tr>
            <tr>
                <td colspan="1">
                    <div class="ansibleOptionAnchor" id="parameter-"></div>
                    <b>state</b>
                    <a class="ansibleOptionLink" href="#parameter-" title="Permalink to this option"></a>
                    <div style="font-size: small">
                        <span style="color: purple">string</span>
                    </div>
                </td>
                <td>
                        <ul style="margin: 0; padding: 0"><b>Choices:</b>
                                    <li>absent</li>
                                    <li>present</li>
                                    <li><div style="color: blue"><b>query</b>&nbsp;&larr;</div></li>
                        </ul>
                </td>
                <td>
                        <div>Define whether the ACL should be present or not.</div>
                        <div>The <code>query</code> state gets the current ACL without changing it, for use in <code>register</code> operations.</div>
                </td>
            </tr>
            <tr>
                <td colspan="1">
                    <div class="ansibleOptionAnchor" id="parameter-"></div>
                    <b>use_nfsv4_acls</b>
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
                        <div>Use NFSv4 ACLs instead of POSIX ACLs.</div>
                </td>
            </tr>
    </table>
    <br/>


Notes
-----

.. note::
   - The ``acl`` module requires that ACLs are enabled on the target filesystem and that the ``setfacl`` and ``getfacl`` binaries are installed.
   - As of Ansible 2.0, this module only supports Linux distributions.
   - As of Ansible 2.3, the *name* option has been changed to *path* as default, but *name* still works as well.



Examples
--------

.. code-block:: yaml

    - name: Grant user Joe read access to a file
      ansible.posix.acl:
        path: /etc/foo.conf
        entity: joe
        etype: user
        permissions: r
        state: present

    - name: Removes the ACL for Joe on a specific file
      ansible.posix.acl:
        path: /etc/foo.conf
        entity: joe
        etype: user
        state: absent

    - name: Sets default ACL for joe on /etc/foo.d/
      ansible.posix.acl:
        path: /etc/foo.d/
        entity: joe
        etype: user
        permissions: rw
        default: yes
        state: present

    - name: Same as previous but using entry shorthand
      ansible.posix.acl:
        path: /etc/foo.d/
        entry: default:user:joe:rw-
        state: present

    - name: Obtain the ACL for a specific file
      ansible.posix.acl:
        path: /etc/foo.conf
      register: acl_info



Return Values
-------------
Common return values are documented `here <https://docs.ansible.com/ansible/latest/reference_appendices/common_return_values.html#common-return-values>`_, the following are the fields unique to this module:

.. raw:: html

    <table border=0 cellpadding=0 class="documentation-table">
        <tr>
            <th colspan="1">Key</th>
            <th>Returned</th>
            <th width="100%">Description</th>
        </tr>
            <tr>
                <td colspan="1">
                    <div class="ansibleOptionAnchor" id="return-"></div>
                    <b>acl</b>
                    <a class="ansibleOptionLink" href="#return-" title="Permalink to this return value"></a>
                    <div style="font-size: small">
                      <span style="color: purple">list</span>
                    </div>
                </td>
                <td>success</td>
                <td>
                            <div>Current ACL on provided path (after changes, if any)</div>
                    <br/>
                        <div style="font-size: smaller"><b>Sample:</b></div>
                        <div style="font-size: smaller; color: blue; word-wrap: break-word; word-break: break-all;">[&#x27;user::rwx&#x27;, &#x27;group::rwx&#x27;, &#x27;other::rwx&#x27;]</div>
                </td>
            </tr>
    </table>
    <br/><br/>


Status
------


Authors
~~~~~~~

- Brian Coca (@bcoca)
- Jérémie Astori (@astorije)
