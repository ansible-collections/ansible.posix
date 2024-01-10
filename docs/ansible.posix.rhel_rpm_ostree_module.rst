.. _ansible.posix.rhel_rpm_ostree_module:


*****************************
ansible.posix.rhel_rpm_ostree
*****************************

**Ensure packages exist in a RHEL for Edge rpm-ostree based system**


Version added: 1.5.0

.. contents::
   :local:
   :depth: 1


Synopsis
--------
- Compatibility layer for using the "package" module for RHEL for Edge systems utilizing the RHEL System Roles.



Requirements
------------
The below requirements are needed on the host that executes this module.

- rpm-ostree


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
                    <b>name</b>
                    <a class="ansibleOptionLink" href="#parameter-" title="Permalink to this option"></a>
                    <div style="font-size: small">
                        <span style="color: purple">list</span>
                         / <span style="color: purple">elements=string</span>
                    </div>
                </td>
                <td>
                        <b>Default:</b><br/><div style="color: blue">[]</div>
                </td>
                <td>
                        <div>A package name or package specifier with version, like <code>name-1.0</code>.</div>
                        <div>Comparison operators for package version are valid here <code>&gt;</code>, <code>&lt;</code>, <code>&gt;=</code>, <code>&lt;=</code>. Example - <code>name&gt;=1.0</code></div>
                        <div>If a previous version is specified, the task also needs to turn <code>allow_downgrade</code> on. See the <code>allow_downgrade</code> documentation for caveats with downgrading packages.</div>
                        <div>When using state=latest, this can be <code>&#x27;*&#x27;</code> which means run <code>yum -y update</code>.</div>
                        <div>You can also pass a url or a local path to a rpm file (using state=present). To operate on several packages this can accept a comma separated string of packages or (as of 2.0) a list of packages.</div>
                        <div style="font-size: small; color: darkgreen"><br/>aliases: pkg</div>
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
                                    <li>installed</li>
                                    <li>latest</li>
                                    <li>present</li>
                                    <li>removed</li>
                        </ul>
                </td>
                <td>
                        <div>Whether to install (<code>present</code> or <code>installed</code>, <code>latest</code>), or remove (<code>absent</code> or <code>removed</code>) a package.</div>
                        <div><code>present</code> and <code>installed</code> will simply ensure that a desired package is installed.</div>
                        <div><code>latest</code> will update the specified package if it&#x27;s not of the latest available version.</div>
                        <div><code>absent</code> and <code>removed</code> will remove the specified package.</div>
                        <div>Default is <code>None</code>, however in effect the default action is <code>present</code> unless the <code>autoremove</code> option is enabled for this module, then <code>absent</code> is inferred.</div>
                </td>
            </tr>
    </table>
    <br/>


Notes
-----

.. note::
   - This module does not support installing or removing packages to/from an overlay as this is not supported by RHEL for Edge, packages needed should be defined in the osbuild Blueprint and provided to Image Builder at build time. This module exists only for ``package`` module compatibility.



Examples
--------

.. code-block:: yaml

    - name: Ensure htop and ansible are installed on rpm-ostree based RHEL
      ansible.posix.rhel_rpm_ostree:
        name:
          - htop
          - ansible
        state: present



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
                    <b>msg</b>
                    <a class="ansibleOptionLink" href="#return-" title="Permalink to this return value"></a>
                    <div style="font-size: small">
                      <span style="color: purple">string</span>
                    </div>
                </td>
                <td>always</td>
                <td>
                            <div>status of rpm transaction</div>
                    <br/>
                        <div style="font-size: smaller"><b>Sample:</b></div>
                        <div style="font-size: smaller; color: blue; word-wrap: break-word; word-break: break-all;">No changes made.</div>
                </td>
            </tr>
    </table>
    <br/><br/>


Status
------


Authors
~~~~~~~

- Adam Miller (@maxamillion)
