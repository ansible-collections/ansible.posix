# ansible.posix
<!-- Add CI and code coverage badges here. Samples included below. -->
[![Run Status](https://api.shippable.com/projects/5e669aaf8b17a60007e4d18d/badge?branch=master)]() [![Codecov](https://img.shields.io/codecov/c/github/ansible-collections/ansible.posix)](https://codecov.io/gh/ansible-collections/ansible.posix)

<!-- Describe the collection and why a user would want to use it. What does the collection do? -->

## Tested with Ansible

<!-- List the versions of Ansible the collection has been tested with. Must match what is in galaxy.yml. -->

* ansible-base 2.10 (devel)

## External requirements

None

## Included content

<!--start collection content-->
### Modules
Name | Description
--- | ---
[ansible.posix.acl](https://github.com/ansible-collections/ansible.posix/blob/master/docs/ansible.posix.acl.rst)|Set and retrieve file ACL information.
[ansible.posix.at](https://github.com/ansible-collections/ansible.posix/blob/master/docs/ansible.posix.at.rst)|Schedule the execution of a command or script file via the at command
[ansible.posix.authorized_key](https://github.com/ansible-collections/ansible.posix/blob/master/docs/ansible.posix.authorized_key.rst)|Adds or removes an SSH authorized key
[ansible.posix.mount](https://github.com/ansible-collections/ansible.posix/blob/master/docs/ansible.posix.mount.rst)|Control active and configured mount points
[ansible.posix.patch](https://github.com/ansible-collections/ansible.posix/blob/master/docs/ansible.posix.patch.rst)|Apply patch files using the GNU patch tool
[ansible.posix.seboolean](https://github.com/ansible-collections/ansible.posix/blob/master/docs/ansible.posix.seboolean.rst)|Toggles SELinux booleans
[ansible.posix.selinux](https://github.com/ansible-collections/ansible.posix/blob/master/docs/ansible.posix.selinux.rst)|Change policy and state of SELinux
[ansible.posix.synchronize](https://github.com/ansible-collections/ansible.posix/blob/master/docs/ansible.posix.synchronize.rst)|A wrapper around rsync to make common tasks in your playbooks quick and easy
[ansible.posix.sysctl](https://github.com/ansible-collections/ansible.posix/blob/master/docs/ansible.posix.sysctl.rst)|Manage entries in sysctl.conf.
<!--end collection content-->

## Using this collection

<!--Include some quick examples that cover the most common use cases for your collection content. -->

See [Ansible Using collections](https://docs.ansible.com/ansible/latest/user_guide/collections_using.html) for more details.

## Contributing to this collection

<!--Describe how the community can contribute to your collection. At a minimum, include how and where users can create issues to report problems or request features for this collection.  List contribution requirements, including preferred workflows and necessary testing, so you can benefit from community PRs. If you are following general Ansible contributor guidelines, you can link to - [Ansible Community Guide](https://docs.ansible.com/ansible/latest/community/index.html). -->

* [Issues](https://github.com/ansible-collections/ansible.posix/issues)
* [Pull Requests](https://github.com/ansible-collections/ansible.posix/pulls)
* [Ansible Community Guide](https://docs.ansible.com/ansible/latest/community/index.html)

## Release notes

* 0.1.1 Initial stable build
* 0.1.0 Internal only build

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

See [LICENCE](https://www.gnu.org/licenses/gpl-3.0.txt) to see the full text.
