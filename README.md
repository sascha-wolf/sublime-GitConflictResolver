Git Conflict Resolver
===========================

A Sublime Text plugin to help you solve this nasty merge conflicts.

Commands
---------

Git Conflict Resolver ships with four commands: `Find Next Conflict`, `Keep Ours`, `Keep Theirs`, `Keep Common Ancestor`.

While most of them are pretty self explaining, the `Keep Common Ancestor` could need some elaboration:
This command is especially useful for the diff3 conflict type of Git. If have no idea what I'm talking about then
[check it out](http://git-scm.com/docs/git-merge) it's great! (Just search for diff3 on the page)

Some clarification:
The first block always represents `our` while the last block is always `theirs`.

There are no default shortcuts, to add them open your user keybindings file and add a keybinding like the following:

    { "keys": ["ctrl+alt+f"], "command": "find_next_conflict" },
    { "keys": ["ctrl+alt+o"], "command": "keep", "args": { "keep": "ours" } },
    { "keys": ["ctrl+alt+t"], "command": "keep", "args": { "keep": "theirs" } },
    { "keys": ["ctrl+alt+a"], "command": "keep", "args": { "keep": "ancestor" } }