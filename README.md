Git Conflict Resolver
===========================

A Sublime Text plugin to help you solve this nasty merge conflicts.

Commands
---------

Git Conflict Resolver ships with three commands: `Find Next Conflict`, `Keep Old`, `Keep New`.

All of them are pretty self explaining. The plugin always consideres the first block as the old block while the second represents the new one.

There are no default shortcuts, to add them open your user keybindings file and add a keybinding like the following:

    { "keys": ["ctrl+alt+f"], "command": "find_next_conflict" },
    { "keys": ["ctrl+alt+o"], "command": "keep_old" },
    { "keys": ["ctrl+alt+n"], "command": "keep_new" }
