import sublime


_plugin_name = "Git Conflict Resolver"
_icon_folder = "/".join([_plugin_name, "gutter"])
_icons = {
    "ours": "ours",
    "ancestor": "ancestor",
    "theirs": "theirs"
}


def get(group):
    base = ""
    extension = ""
    if int(sublime.version()) < 3000:
        base = "/".join(["..", _icon_folder])
    else:
        base = "/".join(["Packages", _icon_folder])
        extension = ".png"

    return "/".join([base, _icons[group] + extension])
