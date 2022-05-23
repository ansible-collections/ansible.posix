.. _ansible.posix.firewalld_module:


***********************
ansible.posix.firewalld
***********************

**Manage arbitrary ports/services with firewalld**



.. contents::
   :local:
   :depth: 1


Synopsis
--------
- This module allows for addition or deletion of services and ports (either TCP or UDP) in either running or permanent firewalld rules.



Requirements
------------
The below requirements are needed on the host that executes this module.

- firewalld >= 0.2.11
- python-firewall >= 0.2.11


Parameters
----------

.. raw:: html

    <table  border=0 cellpadding=0 class="documentation-table">
        <tr>
            <th colspan="2">Parameter</th>
            <th>Choices/<font color="blue">Defaults</font></th>
            <th width="100%">Comments</th>
        </tr>
            <tr>
                <td colspan="2">
                    <div class="ansibleOptionAnchor" id="parameter-"></div>
                    <b>icmp_block</b>
                    <a class="ansibleOptionLink" href="#parameter-" title="Permalink to this option"></a>
                    <div style="font-size: small">
                        <span style="color: purple">string</span>
                    </div>
                </td>
                <td>
                </td>
                <td>
                        <div>The ICMP block you would like to add/remove to/from a zone in firewalld.</div>
                </td>
            </tr>
            <tr>
                <td colspan="2">
                    <div class="ansibleOptionAnchor" id="parameter-"></div>
                    <b>icmp_block_inversion</b>
                    <a class="ansibleOptionLink" href="#parameter-" title="Permalink to this option"></a>
                    <div style="font-size: small">
                        <span style="color: purple">string</span>
                    </div>
                </td>
                <td>
                </td>
                <td>
                        <div>Enable/Disable inversion of ICMP blocks for a zone in firewalld.</div>
                </td>
            </tr>
            <tr>
                <td colspan="2">
                    <div class="ansibleOptionAnchor" id="parameter-"></div>
                    <b>immediate</b>
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
                        <div>Should this configuration be applied immediately, if set as permanent.</div>
                </td>
            </tr>
            <tr>
                <td colspan="2">
                    <div class="ansibleOptionAnchor" id="parameter-"></div>
                    <b>interface</b>
                    <a class="ansibleOptionLink" href="#parameter-" title="Permalink to this option"></a>
                    <div style="font-size: small">
                        <span style="color: purple">string</span>
                    </div>
                </td>
                <td>
                </td>
                <td>
                        <div>The interface you would like to add/remove to/from a zone in firewalld.</div>
                </td>
            </tr>
            <tr>
                <td colspan="2">
                    <div class="ansibleOptionAnchor" id="parameter-"></div>
                    <b>masquerade</b>
                    <a class="ansibleOptionLink" href="#parameter-" title="Permalink to this option"></a>
                    <div style="font-size: small">
                        <span style="color: purple">string</span>
                    </div>
                </td>
                <td>
                </td>
                <td>
                        <div>The masquerade setting you would like to enable/disable to/from zones within firewalld.</div>
                </td>
            </tr>
            <tr>
                <td colspan="2">
                    <div class="ansibleOptionAnchor" id="parameter-"></div>
                    <b>offline</b>
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
                        <div>Whether to run this module even when firewalld is offline.</div>
                </td>
            </tr>
            <tr>
                <td colspan="2">
                    <div class="ansibleOptionAnchor" id="parameter-"></div>
                    <b>permanent</b>
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
                        <div>Should this configuration be in the running firewalld configuration or persist across reboots.</div>
                        <div>As of Ansible 2.3, permanent operations can operate on firewalld configs when it is not running (requires firewalld &gt;= 0.3.9).</div>
                        <div>Note that if this is <code>no</code>, immediate is assumed <code>yes</code>.</div>
                </td>
            </tr>
            <tr>
                <td colspan="2">
                    <div class="ansibleOptionAnchor" id="parameter-"></div>
                    <b>port</b>
                    <a class="ansibleOptionLink" href="#parameter-" title="Permalink to this option"></a>
                    <div style="font-size: small">
                        <span style="color: purple">string</span>
                    </div>
                </td>
                <td>
                </td>
                <td>
                        <div>Name of a port or port range to add/remove to/from firewalld.</div>
                        <div>Must be in the form PORT/PROTOCOL or PORT-PORT/PROTOCOL for port ranges.</div>
                </td>
            </tr>
            <tr>
                <td colspan="2">
                    <div class="ansibleOptionAnchor" id="parameter-"></div>
                    <b>port_forward</b>
                    <a class="ansibleOptionLink" href="#parameter-" title="Permalink to this option"></a>
                    <div style="font-size: small">
                        <span style="color: purple">list</span>
                         / <span style="color: purple">elements=dictionary</span>
                    </div>
                </td>
                <td>
                </td>
                <td>
                        <div>Port and protocol to forward using firewalld.</div>
                </td>
            </tr>
                                <tr>
                    <td class="elbow-placeholder"></td>
                <td colspan="1">
                    <div class="ansibleOptionAnchor" id="parameter-"></div>
                    <b>port</b>
                    <a class="ansibleOptionLink" href="#parameter-" title="Permalink to this option"></a>
                    <div style="font-size: small">
                        <span style="color: purple">string</span>
                         / <span style="color: red">required</span>
                    </div>
                </td>
                <td>
                </td>
                <td>
                        <div>Source port to forward from</div>
                </td>
            </tr>
            <tr>
                    <td class="elbow-placeholder"></td>
                <td colspan="1">
                    <div class="ansibleOptionAnchor" id="parameter-"></div>
                    <b>proto</b>
                    <a class="ansibleOptionLink" href="#parameter-" title="Permalink to this option"></a>
                    <div style="font-size: small">
                        <span style="color: purple">string</span>
                         / <span style="color: red">required</span>
                    </div>
                </td>
                <td>
                        <ul style="margin: 0; padding: 0"><b>Choices:</b>
                                    <li>udp</li>
                                    <li>tcp</li>
                        </ul>
                </td>
                <td>
                        <div>protocol to forward</div>
                </td>
            </tr>
            <tr>
                    <td class="elbow-placeholder"></td>
                <td colspan="1">
                    <div class="ansibleOptionAnchor" id="parameter-"></div>
                    <b>toaddr</b>
                    <a class="ansibleOptionLink" href="#parameter-" title="Permalink to this option"></a>
                    <div style="font-size: small">
                        <span style="color: purple">string</span>
                    </div>
                </td>
                <td>
                </td>
                <td>
                        <div>Optional address to forward to</div>
                </td>
            </tr>
            <tr>
                    <td class="elbow-placeholder"></td>
                <td colspan="1">
                    <div class="ansibleOptionAnchor" id="parameter-"></div>
                    <b>toport</b>
                    <a class="ansibleOptionLink" href="#parameter-" title="Permalink to this option"></a>
                    <div style="font-size: small">
                        <span style="color: purple">string</span>
                         / <span style="color: red">required</span>
                    </div>
                </td>
                <td>
                </td>
                <td>
                        <div>destination port</div>
                </td>
            </tr>

            <tr>
                <td colspan="2">
                    <div class="ansibleOptionAnchor" id="parameter-"></div>
                    <b>rich_rule</b>
                    <a class="ansibleOptionLink" href="#parameter-" title="Permalink to this option"></a>
                    <div style="font-size: small">
                        <span style="color: purple">string</span>
                    </div>
                </td>
                <td>
                </td>
                <td>
                        <div>Rich rule to add/remove to/from firewalld.</div>
                        <div>See <a href='https://firewalld.org/documentation/man-pages/firewalld.richlanguage.html'>Syntax for firewalld rich language rules</a>.</div>
                </td>
            </tr>
            <tr>
                <td colspan="2">
                    <div class="ansibleOptionAnchor" id="parameter-"></div>
                    <b>service</b>
                    <a class="ansibleOptionLink" href="#parameter-" title="Permalink to this option"></a>
                    <div style="font-size: small">
                        <span style="color: purple">string</span>
                    </div>
                </td>
                <td>
                </td>
                <td>
                        <div>Name of a service to add/remove to/from firewalld.</div>
                        <div>The service must be listed in output of firewall-cmd --get-services.</div>
                </td>
            </tr>
            <tr>
                <td colspan="2">
                    <div class="ansibleOptionAnchor" id="parameter-"></div>
                    <b>source</b>
                    <a class="ansibleOptionLink" href="#parameter-" title="Permalink to this option"></a>
                    <div style="font-size: small">
                        <span style="color: purple">string</span>
                    </div>
                </td>
                <td>
                </td>
                <td>
                        <div>The source/network you would like to add/remove to/from firewalld.</div>
                </td>
            </tr>
            <tr>
                <td colspan="2">
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
                                    <li>disabled</li>
                                    <li>enabled</li>
                                    <li>present</li>
                        </ul>
                </td>
                <td>
                        <div>Enable or disable a setting.</div>
                        <div>For ports: Should this port accept (enabled) or reject (disabled) connections.</div>
                        <div>The states <code>present</code> and <code>absent</code> can only be used in zone level operations (i.e. when no other parameters but zone and state are set).</div>
                </td>
            </tr>
            <tr>
                <td colspan="2">
                    <div class="ansibleOptionAnchor" id="parameter-"></div>
                    <b>target</b>
                    <a class="ansibleOptionLink" href="#parameter-" title="Permalink to this option"></a>
                    <div style="font-size: small">
                        <span style="color: purple">string</span>
                    </div>
                    <div style="font-style: italic; font-size: small; color: darkgreen">added in 1.2.0</div>
                </td>
                <td>
                        <ul style="margin: 0; padding: 0"><b>Choices:</b>
                                    <li>default</li>
                                    <li>ACCEPT</li>
                                    <li>DROP</li>
                                    <li>%%REJECT%%</li>
                        </ul>
                </td>
                <td>
                        <div>firewalld Zone target</div>
                        <div>If state is set to <code>absent</code>, this will reset the target to default</div>
                </td>
            </tr>
            <tr>
                <td colspan="2">
                    <div class="ansibleOptionAnchor" id="parameter-"></div>
                    <b>timeout</b>
                    <a class="ansibleOptionLink" href="#parameter-" title="Permalink to this option"></a>
                    <div style="font-size: small">
                        <span style="color: purple">integer</span>
                    </div>
                </td>
                <td>
                        <b>Default:</b><br/><div style="color: blue">0</div>
                </td>
                <td>
                        <div>The amount of time in seconds the rule should be in effect for when non-permanent.</div>
                </td>
            </tr>
            <tr>
                <td colspan="2">
                    <div class="ansibleOptionAnchor" id="parameter-"></div>
                    <b>zone</b>
                    <a class="ansibleOptionLink" href="#parameter-" title="Permalink to this option"></a>
                    <div style="font-size: small">
                        <span style="color: purple">string</span>
                    </div>
                </td>
                <td>
                </td>
                <td>
                        <div>The firewalld zone to add/remove to/from.</div>
                        <div>Note that the default zone can be configured per system but <code>public</code> is default from upstream.</div>
                        <div>Available choices can be extended based on per-system configs, listed here are &quot;out of the box&quot; defaults.</div>
                        <div>Possible values include <code>block</code>, <code>dmz</code>, <code>drop</code>, <code>external</code>, <code>home</code>, <code>internal</code>, <code>public</code>, <code>trusted</code>, <code>work</code>.</div>
                </td>
            </tr>
    </table>
    <br/>


Notes
-----

.. note::
   - Not tested on any Debian based system.
   - Requires the python2 bindings of firewalld, which may not be installed by default.
   - For distributions where the python2 firewalld bindings are unavailable (e.g Fedora 28 and later) you will have to set the ansible_python_interpreter for these hosts to the python3 interpreter path and install the python3 bindings.
   - Zone transactions (creating, deleting) can be performed by using only the zone and state parameters "present" or "absent". Note that zone transactions must explicitly be permanent. This is a limitation in firewalld. This also means that you will have to reload firewalld after adding a zone that you wish to perform immediate actions on. The module will not take care of this for you implicitly because that would undo any previously performed immediate actions which were not permanent. Therefore, if you require immediate access to a newly created zone it is recommended you reload firewalld immediately after the zone creation returns with a changed state and before you perform any other immediate, non-permanent actions on that zone.
   - This module needs ``python-firewall`` or ``python3-firewall`` on managed nodes. It is usually provided as a subset with ``firewalld`` from the OS distributor for the OS default Python interpreter.



Examples
--------

.. code-block:: yaml

    - name: permit traffic in default zone for https service
      ansible.posix.firewalld:
        service: https
        permanent: yes
        state: enabled

    - name: do not permit traffic in default zone on port 8081/tcp
      ansible.posix.firewalld:
        port: 8081/tcp
        permanent: yes
        state: disabled

    - ansible.posix.firewalld:
        port: 161-162/udp
        permanent: yes
        state: enabled

    - ansible.posix.firewalld:
        zone: dmz
        service: http
        permanent: yes
        state: enabled

    - ansible.posix.firewalld:
        rich_rule: rule service name="ftp" audit limit value="1/m" accept
        permanent: yes
        state: enabled

    - ansible.posix.firewalld:
        source: 192.0.2.0/24
        zone: internal
        state: enabled

    - ansible.posix.firewalld:
        zone: trusted
        interface: eth2
        permanent: yes
        state: enabled

    - ansible.posix.firewalld:
        masquerade: yes
        state: enabled
        permanent: yes
        zone: dmz

    - ansible.posix.firewalld:
        zone: custom
        state: present
        permanent: yes

    - ansible.posix.firewalld:
        zone: drop
        state: enabled
        permanent: yes
        icmp_block_inversion: yes

    - ansible.posix.firewalld:
        zone: drop
        state: enabled
        permanent: yes
        icmp_block: echo-request

    - ansible.posix.firewalld:
        zone: internal
        state: present
        permanent: yes
        target: ACCEPT

    - name: Redirect port 443 to 8443 with Rich Rule
      ansible.posix.firewalld:
        rich_rule: rule family=ipv4 forward-port port=443 protocol=tcp to-port=8443
        zone: public
        permanent: yes
        immediate: yes
        state: enabled




Status
------


Authors
~~~~~~~

- Adam Miller (@maxamillion)
