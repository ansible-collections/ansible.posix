.. _ansible.posix.rhel_facts_module:


************************
ansible.posix.rhel_facts
************************

**Facts module to set or override RHEL specific facts.**


Version added: 1.5.0

.. contents::
   :local:
   :depth: 1


Synopsis
--------
- Compatibility layer for using the "package" module for rpm-ostree based systems via setting the "pkg_mgr" fact correctly.



Requirements
------------
The below requirements are needed on the host that executes this module.

- rpm-ostree




See Also
--------

.. seealso::

   :ref:`ansible.builtin.package_module`
      The official documentation on the **ansible.builtin.package** module.


Examples
--------

.. code-block:: yaml

    - name: Playbook to use the package module on all RHEL footprints
      vars:
        ansible_facts_modules:
          - setup # REQUIRED to be run before all custom fact modules
          - ansible.posix.rhel_facts
      tasks:
        - name: Ensure packages are installed
          ansible.builtin.package:
            name:
              - htop
              - ansible
            state: present


Returned Facts
--------------
Facts returned by this module are added/updated in the ``hostvars`` host facts and can be referenced by name just like any other host fact. They do not need to be registered in order to use them.

.. raw:: html

    <table border=0 cellpadding=0 class="documentation-table">
                    <tr>
            <th colspan="1">Fact</th>
            <th>Returned</th>
            <th width="100%">Description</th>
        </tr>
            <tr>
                <td colspan="1" colspan="1">
                    <div class="ansibleOptionAnchor" id="return-"></div>
                    <b>pkg_mgr</b>
                    <a class="ansibleOptionLink" href="#return-" title="Permalink to this fact"></a>
                    <div style="font-size: small">
                      <span style="color: purple">string</span>
                    </div>
                </td>
                <td>when needed</td>
                <td>
                            <div>System-level package manager override
                            </div>
                    <br/>
                        <div style="font-size: smaller"><b>Sample:</b></div>
                        <div style="font-size: smaller; color: blue; word-wrap: break-word; word-break: break-all;">{&#x27;pkg_mgr&#x27;: &#x27;ansible.posix.rhel_facts&#x27;}</div>
                </td>
            </tr>
    </table>
    <br/><br/>



Status
------


Authors
~~~~~~~

- Adam Miller (@maxamillion)
