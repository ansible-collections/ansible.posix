# ansible.posix
<!-- Add CI and code coverage badges here. Samples included below. -->
[![Build Status](
https://dev.azure.com/ansible/ansible.posix/_apis/build/status/CI?branchName=main)](https://dev.azure.com/ansible/ansible.posix/_build?definitionId=26)
[![Run Status](https://api.shippable.com/projects/5e669aaf8b17a60007e4d18d/badge?branch=main)]() <!--[![Codecov](https://img.shields.io/codecov/c/github/ansible-collections/ansible.posix)](https://codecov.io/gh/ansible-collections/ansible.posix)-->

<!-- Describe the collection and why a user would want to use it. What does the collection do? -->
An Ansible Collection of modules and plugins that target POSIX UNIX/Linux and derivative Operating Systems.

## Supported Versions of Ansible
<!--start requires_ansible-->
## Ansible version compatibility

This collection has been tested against following Ansible versions: **>=2.14**.
<!--end requires_ansible-->

## Included content
<!-- Galaxy will eventually list the module docs within the UI, but until that is ready, you may need to either describe your plugins etc here, or point to an external docsite to cover that information. -->
<!--start collection content-->
### Modules
Name | Description
--- | ---
[ansible.posix.acl](https://github.com/ansible-collections/ansible.posix/blob/main/docs/ansible.posix.acl_module.rst)|Set and retrieve file ACL information.
[ansible.posix.at](https://github.com/ansible-collections/ansible.posix/blob/main/docs/ansible.posix.at_module.rst)|Schedule the execution of a command or script file via the at command
[ansible.posix.authorized_key](https://github.com/ansible-collections/ansible.posix/blob/main/docs/ansible.posix.authorized_key_module.rst)|Adds or removes an SSH authorized key
[ansible.posix.firewalld](https://github.com/ansible-collections/ansible.posix/blob/main/docs/ansible.posix.firewalld_module.rst)|Manage arbitrary ports/services with firewalld
[ansible.posix.firewalld_info](https://github.com/ansible-collections/ansible.posix/blob/main/docs/ansible.posix.firewalld_info_module.rst)|Gather information about firewalld
[ansible.posix.mount](https://github.com/ansible-collections/ansible.posix/blob/main/docs/ansible.posix.mount_module.rst)|Control active and configured mount points
[ansible.posix.patch](https://github.com/ansible-collections/ansible.posix/blob/main/docs/ansible.posix.patch_module.rst)|Apply patch files using the GNU patch tool
[ansible.posix.rhel_facts](https://github.com/ansible-collections/ansible.posix/blob/main/docs/ansible.posix.rhel_facts_module.rst)|Facts module to set or override RHEL specific facts.
[ansible.posix.rhel_rpm_ostree](https://github.com/ansible-collections/ansible.posix/blob/main/docs/ansible.posix.rhel_rpm_ostree_module.rst)|Ensure packages exist in a RHEL for Edge rpm-ostree based system
[ansible.posix.rpm_ostree_upgrade](https://github.com/ansible-collections/ansible.posix/blob/main/docs/ansible.posix.rpm_ostree_upgrade_module.rst)|Manage rpm-ostree upgrade transactions
[ansible.posix.seboolean](https://github.com/ansible-collections/ansible.posix/blob/main/docs/ansible.posix.seboolean_module.rst)|Toggles SELinux booleans
[ansible.posix.selinux](https://github.com/ansible-collections/ansible.posix/blob/main/docs/ansible.posix.selinux_module.rst)|Change policy and state of SELinux
[ansible.posix.synchronize](https://github.com/ansible-collections/ansible.posix/blob/main/docs/ansible.posix.synchronize_module.rst)|A wrapper around rsync to make common tasks in your playbooks quick and easy
[ansible.posix.sysctl](https://github.com/ansible-collections/ansible.posix/blob/main/docs/ansible.posix.sysctl_module.rst)|Manage entries in sysctl.conf.

<!--end collection content-->

## Installing this collection

You can install the ``ansible.posix`` collection with the Ansible Galaxy CLI:

    ansible-galaxy collection install ansible.posix

You can also include it in a `requirements.yml` file and install it with `ansible-galaxy collection install -r requirements.yml`, using the format:

```yaml
---
collections:
  - name: ansible.posix
```

## Using this collection

<!--Include some quick examples that cover the most common use cases for your collection content. -->

See [Ansible Using collections](https://docs.ansible.com/ansible/latest/user_guide/collections_using.html) for more details.

## Contributing to this collection

<!--Describe how the community can contribute to your collection. At a minimum, include how and where users can create issues to report problems or request features for this collection.  List contribution requirements, including preferred workflows and necessary testing, so you can benefit from community PRs. If you are following general Ansible contributor guidelines, you can link to - [Ansible Community Guide](https://docs.ansible.com/ansible/latest/community/index.html). -->

We welcome community contributions to this collection. See [Contributing to Ansible-maintained collections](https://docs.ansible.com/ansible/devel/community/contributing_maintained_collections.html#contributing-maintained-collections) for complete details.

* [Issues](https://github.com/ansible-collections/ansible.posix/issues)
* [Pull Requests](https://github.com/ansible-collections/ansible.posix/pulls)
* [Ansible Community Guide](https://docs.ansible.com/ansible/latest/community/index.html)

### Code of Conduct
This collection follows the Ansible project's
[Code of Conduct](https://docs.ansible.com/ansible/devel/community/code_of_conduct.html).
Please read and familiarize yourself with this document.

## Release notes
See [changelog](https://github.com/ansible-collections/ansible.posix/blob/main/CHANGELOG.rst) for more details.

## External requirements

None

## Tested with Ansible

<!-- List the versions of Ansible the collection has been tested with. Must match what is in galaxy.yml. -->

- ansible-core 2.17 (devel)
- ansible-core 2.16 (stable)
- ansible-core 2.15 (stable)
- ansible-core 2.14 (stable)

## Roadmap

<!-- Optional. Include the roadmap for this collection, and the proposed release/versioning strategy so users can anticipate the upgrade/update cycle. -->

## More information

<!-- List out where the user can find additional information, such as working group meeting times, slack/IRC channels, or documentation for the product this collection automates. At a minimum, link to: -->

- [Ansible Collection overview](https://github.com/ansible-collections/overview)
- [Ansible User guide](https://docs.ansible.com/ansible/latest/user_guide/index.html)
- [Ansible Developer guide](https://docs.ansible.com/ansible/latest/dev_guide/index.html)
- [Ansible Community code of conduct](https://docs.ansible.com/ansible/latest/community/code_of_conduct.html)

## Licensing

GNU General Public License v3.0 or later.

See [COPYING](https://www.gnu.org/licenses/gpl-3.0.txt) to see the full text.
