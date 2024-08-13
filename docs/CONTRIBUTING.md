# How to contribute

Thank you for investing your time in contributing to our project!

First, we recommended reading these if you are not familair with developing modules/collections yet:

[Developing Modules General](https://docs.ansible.com/ansible/latest/dev_guide/developing_modules_general.html)

[Developing Modules Best Practices](https://docs.ansible.com/ansible/latest/dev_guide/developing_modules_best_practices.html)

[Ansible module architecture](https://docs.ansible.com/ansible/latest/dev_guide/developing_program_flow_modules.html)

---

## Issues

### Solve an issue

See [existing issues](https://github.com/cisco-open/ansible-collection-catalystwan/issues) and feel free to work on any.

### Create a new issue

Firstly [search if an issue already exists](https://github.com/cisco-open/ansible-collection-catalystwan/issues).

If issue related to your problem/feature request doesn't exist, create new issue.
There are 3 issue types:

- Bug report
- Feature Request
- Report a security vulnerability

Select one from [issue form](https://github.com/cisco-open/ansible-collection-catalystwan/issues/new/choose).

### Create PR

When you're finished with the changes, create a pull request, also known as a PR.

---

## Development

Initial note: we are using `catalystwan` version that is still under development so please adjust your poetry according to this information.
Sorry for inconvenience but we will fix that soon.

Preferred way to setup environment for development:

1. Use `poetry install` and `poetry shell`
2. Install local collection with `ansible-galaxy collection install . --force`
3. Adjust configuration of variables in ``.dev_dir/dev_vars.yml``
4. Run playground playbook with `ansible-playbook .dev_dir/playground.yml` or any other playbook used for tests

You can also refer to [Ansible modules dev guide](https://docs.ansible.com/ansible/latest/dev_guide/developing_modules_general.html#verifying-your-module-code) to look for more convenient way of
testing your code.

### Dependencies in requirements.txt

All dependencies are updated via `poetry` tool. Dependencies defined for development are later used to generate `requirements.txt` file with command:

```bash
poetry export --without-hashes --format=requirements.txt > requirements.txt
```

---

## Release process

According to [release workflow inside .github workflows](https://github.com/cisco-open/ansible-collection-catalystwan/blob/main/.github/workflows/release-from-tag.yml) collection publication to Ansible Galaxy will happen when admin of the repository will push new tag.
This tag must much version used in [galaxy.yml](../galaxy.yml) file.
Release will happen only if desired version was not published on Ansible Galaxy yet.
