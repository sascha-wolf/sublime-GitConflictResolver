import sublime

_settings_file = "GitConflictResolver.sublime-settings"
_subl_settings = {}
_default_settings = {
    "live_matching": True,
    "matching_scope": 'invalid',
    "fill_conflict_area": False,
    "outline_conflict_area": True,
    "ours_gutter": True,
    "ancestor_gutter": True,
    "theirs_gutter": True,
    "git_path": "git",
    "show_only_filenames": True
}


def load():
    global _subl_settings

    _subl_settings = sublime.load_settings(_settings_file)


def get(key):
    return _subl_settings.get(key, _default_settings[key])
