import sublime

from os import path


_plugin_name = "Git Conflict Resolver"
_icon_folder = path.join(_plugin_name, "gutter")
_icons = {
    "ours": "ours",
    "ancestor": "ancestor",
    "theirs": "theirs"
}


def get(group):
    base = ""
    extension = ""
    if int(sublime.version()) < 3000:
        base = path.join("..", _icon_folder)
    else:
        base = path.join("Packages", _icon_folder)
        extension = ".png"

    return path.join(base, _icons[group] + extension)
