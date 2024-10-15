# ansible.posix
<!-- Add CI and code coverage badges here. Samples included below. -->
[![Build Status](
https://dev.azure.com/ansible/ansible.posix/_apis/build/status/CI?branchName=main)](https://dev.azure.com/ansible/ansible.posix/_build?definitionId=26)
[![Run Status](https://api.shippable.com/projects/5e669aaf8b17a60007e4d18d/badge?branch=main)]() <!--[![Codecov](https://img.shields.io/codecov/c/github/ansible-collections/ansible.posix)](https://codecov.io/gh/ansible-collections/ansible.posix)-->

<!-- Describe the collection and why a user would want to use it. What does the collection do? -->
An Ansible Collection of modules and plugins that target POSIX UNIX/Linux and derivative Operating Systems.

## Communication

* Join the Ansible forum:
  * [Get Help](https://forum.ansible.com/c/help/6): get help or help others.
  * [Social Spaces](https://forum.ansible.com/c/chat/4): gather and interact with fellow enthusiasts.
  * [News & Announcements](https://forum.ansible.com/c/news/5): track project-wide announcements including social events.

* The Ansible [Bullhorn newsletter](https://docs.ansible.com/ansible/devel/community/communication.html#the-bullhorn): used to announce releases and important changes.

For more information about communication, see the [Ansible communication guide](https://docs.ansible.com/ansible/devel/community/communication.html).

## Supported Versions of Ansible
<!--start requires_ansible-->
## Ansible version compatibility

This collection has been tested against following Ansible versions: **>=2.15**.
<!--end requires_ansible-->

## Included content
Check out [Ansible Galaxy](https://galaxy.ansible.com/ui/repo/published/ansible/posix/content/) or [the Ansible documentation](https://docs.ansible.com/ansible/devel/collections/ansible/posix/) for all modules and plugins included in this collection.

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

- ansible-core 2.19 (devel)
- ansible-core 2.18 (stable) *
- ansible-core 2.17 (stable)
- ansible-core 2.16 (stable)
- ansible-core 2.15 (stable)

*Note: For ansible-core 2.18, CI only covers sanity tests and no integration tests will be run until the test environment is released.*

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
