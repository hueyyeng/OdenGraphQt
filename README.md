# OdenGraphQt

OdenGraphQt is a fork of jchanvfx [NodeGraphQt](https://github.com/jchanvfx/NodeGraphQt), a node graph UI framework
for `PySide6` that can be implemented and re-purposed into applications.

## Changes from NodeGraphQt

- **PySide6** compatibility (I have not tested PyQt6) courtesy of **jowr** and **rajkundu**
- Alternative port accept/reject connection
- Partial type hints for IDE type checker (e.g. PyCharm)
- Minor code reformat, tweaks and comments for code readability

## Install

For now, please install as editable package. I'll be publishing to PyPI after I'm done with a few rounds of sanity
testing.

## Documentation

Please refer to jchanvfx excellent documentation at https://chantonic.com/NodeGraphQt/api/index.html

I'll update this section in the near future after re-configuring the `sphinx_doc_build.yml`.

See the [basic_example.py](/examples/basic_example.py) script to get started
or [accept_reject_example.py](/examples/accept_reject_example.py) for the alternative port accept/reject connection
logic.
