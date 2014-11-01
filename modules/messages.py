_messages = {
    "no_conflict_found": "No conflict found",
    "no_conflict_files_found": "No conflict found ({})",
    "no_git_repo_found": "No git repository found",
    "no_such_group": "No such conflict group found",
    "git_executable_not_found": "Git Conflict Resolver is not able find your git executable.\n\n" +
                                "To ensure the plugin works properly you can use the settings file to tell Git Conflict Resolver about the path.\n" +
                                "(Preferences > Package Settings > Git Conflict Resolver > Settings - User)",
    "open_all": "Open all ..."
}


def get(key, *args):
    return str.format(_messages[key], *args)
