Git Conflict Resolver
===========================

A Sublime Text plugin to help you solve this nasty merge conflicts.

Commands
---------

Git Conflict Resolver ships with four commands: `Find Next Conflict`, `Keep Ours`, `Keep Theirs`, `Keep Common Ancestor`.

All of them are pretty self explaining. The `Keep Common Ancestor` is especially interesting for the diff3 conflict type.

The first block always represents `our` while the last block is always `theirs`.

There are no default shortcuts, to add them open your user keybindings file and add a keybinding like the following:

    { "keys": ["ctrl+alt+f"], "command": "find_next_conflict" },
    { "keys": ["ctrl+alt+o"], "command": "keep", "args": { "keep": "ours" } },
    { "keys": ["ctrl+alt+t"], "command": "keep", "args": { "keep": "theirs" } },
    { "keys": ["ctrl+alt+a"], "command": "keep", "args": { "keep": "ancestor" } }
