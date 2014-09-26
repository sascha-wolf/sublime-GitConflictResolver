import sublime
import sublime_plugin
import os
import re
import subprocess

# view.find sadly can't handle naming groups
NO_NAMING_GROUPS_PATTERN = r"(?s)<{7}[^\n]*\n"\
                            "(.*?)(?:\|{7}[^\n]*\n"\
                            "(.*?))?={7}\n(.*?)>{7}[^\n]*\n"

CONFLICT_REGEX = re.compile(r"(?s)<{7}[^\n]*\n"
                            "(?P<ours>.*?)(?:\|{7}[^\n]*\n"
                            "(?P<ancestor>.*?))?={7}\n"
                            "(?P<theirs>.*?)>{7}[^\n]*\n")

# group patterns; this patterns always match the seperating lines too,
# so we have to remove then later from the matched regions
CONFLICT_GROUP_REGEX = {
    "ours": r"(?s)<{7}[^\n]*\n.*?\|{7}|>{7}",
    "ancestor": r"(?s)\|{7}[^\n]*\n.*?={7}",
    "theirs": r"(?s)={7}[^\n]*\n.*?>{7}"
}

icons = {
    "ours": "Packages/Git Conflict Resolver/gutter/ours.png",
    "ancestor": "Packages/Git Conflict Resolver/gutter/ancestor.png",
    "theirs": "Packages/Git Conflict Resolver/gutter/theirs.png"
}

messages = {
    "no_conflict_found": "No conflict found",
    "no_git_repo_found": "No git repository found",
    "no_such_group": "No such conflict group found",
    "open_all": "Open all ..."
}

# Global settings
settings_file = "GitConflictResolver.sublime-settings"
settings = {}
default_settings = {
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


def plugin_loaded():
    global subl_settings, settings

    subl_settings = sublime.load_settings(settings_file)

    # Live matching
    settings['live_matching'] = subl_settings.get(
        'live_matching',
        default_settings['live_matching']
    )
    # Matching scope
    settings['matching_scope'] = subl_settings.get(
        'matching_scope',
        default_settings['matching_scope']
    )
    # Fill conflict area
    settings['fill_conflict_area'] = subl_settings.get(
        'fill_conflict_area',
        default_settings['fill_conflict_area']
    )
    # Outline conflict area
    settings['outline_conflict_area'] = subl_settings.get(
        'outline_conflict_area',
        default_settings['outline_conflict_area']
    )
    # Conflict group highlighting
    settings['ours_gutter'] = subl_settings.get(
        'ours_gutter',
        default_settings['ours_gutter']
    )
    settings['ancestor_gutter'] = subl_settings.get(
        'ancestor_gutter',
        default_settings['ancestor_gutter']
    )
    settings['theirs_gutter'] = subl_settings.get(
        'theirs_gutter',
        default_settings['theirs_gutter']
    )

    # Git Settings
    settings['git_path'] = subl_settings.get(
        'git_path',
        default_settings['git_path']
    )

    # Remove everything except for the part from the filename
    settings['show_only_filenames'] = subl_settings.get(
        'show_only_filenames',
        default_settings['show_only_filenames']
    )


def find_conflict(view, begin=0):
    conflict_region = view.find(NO_NAMING_GROUPS_PATTERN, begin)

    if not conflict_region:
        conflict_region = view.find(NO_NAMING_GROUPS_PATTERN, 0)
        if not conflict_region:
            sublime.status_message(messages['no_conflict_found'])
            return None

    return conflict_region


def join_regions(regions):
    if not regions:
        return sublime.Region(-1, -1)

    begin = min([region.begin() for region in regions if region.begin() >= 0])
    end = max([region.end() for region in regions])

    return sublime.Region(begin, end)


def highlight_conflict_group(view, group):
    scope = group + '_gutter'
    if settings[scope]:
        conflict_regions = view.find_all(CONFLICT_GROUP_REGEX[group])

        if not conflict_regions:
            return

        # Remove the first and last line since they just contain the separators
        highlight_regions = []
        for region in conflict_regions:
            region = view.split_by_newlines(region)[1:-1]
            # Ignore empty subregions
            if not region:
                continue

            for subregion in region:
                highlight_regions.append(subregion)

        view.erase_regions("GitConflictRegion_" + group)
        view.add_regions(
            "GitConflictRegions_" + group,
            highlight_regions,
            "warning",
            icons[group],
            sublime.DRAW_NO_FILL |
            sublime.DRAW_NO_OUTLINE |
            sublime.HIDE_ON_MINIMAP
        )


def highlight_conflicts(view):
    conflict_regions = view.find_all(NO_NAMING_GROUPS_PATTERN)

    view.erase_regions("GitConflictRegions")
    view.add_regions(
        "GitConflictRegions",
        conflict_regions,
        settings['matching_scope'],
        "",
        (0 if settings['fill_conflict_area'] else sublime.DRAW_NO_FILL)
        |
        (0 if settings['outline_conflict_area'] else sublime.DRAW_NO_OUTLINE)
    )

    highlight_conflict_group(view, 'ours')
    highlight_conflict_group(view, 'ancestor')
    highlight_conflict_group(view, 'theirs')


def extract(view, region, keep):
    conflict_text = view.substr(region)
    match = CONFLICT_REGEX.search(conflict_text)

    # If we didn't matched the group return None
    if not match.group(keep):
        sublime.status_message(messages['no_such_group'])
        return None

    return CONFLICT_REGEX.sub(r'\g<' + keep + '>', conflict_text)


class FindNextConflict(sublime_plugin.TextCommand):
    def run(self, edit):
        current_selection = self.view.sel()

        # Use the end of the current selection for the search, or use 0 if nothing is selected
        begin = 0
        if len(current_selection) > 0:
            begin = self.view.sel()[-1].end()

        conflict_region = find_conflict(self.view, begin)
        if conflict_region is None:
            return

        # Add the region to the selection
        self.view.show_at_center(conflict_region)
        current_selection.clear()
        current_selection.add(conflict_region)


class Keep(sublime_plugin.TextCommand):
    def run(self, edit, keep):
        current_selection = self.view.sel()

        # Use the begin of the current selection for the search, or use 0 if nothing is selected
        begin = 0
        if len(current_selection) > 0:
            begin = current_selection[0].begin()

        conflict_region = find_conflict(self.view, begin)
        if conflict_region is None:
            return

        replace_text = extract(self.view, conflict_region, keep)

        if not replace_text:
            replace_text = ""

        self.view.replace(edit, conflict_region, replace_text)


class ListConflictFiles(sublime_plugin.WindowCommand):
    def run(self):
        window = self.window
        git_repo = self._determine_git_dir()
        if not git_repo:
            sublime.status_message(messages['no_git_repo_found'])
            return

        conflict_files = self._get_conflict_files(git_repo)

        if not conflict_files:
            sublime.status_message(
                messages['no_conflict_found'] +
                ((" (" + git_repo + ")") if git_repo else "")
            )
            return

        conflict_files = conflict_files.split('\n')
        # Remove empty strings and sort the list
        # (TODO: sort also filenames only?)
        conflict_files = sorted([x for x in conflict_files if x])

        # Copy the list for representation
        show_files = list(conflict_files)

        if settings['show_only_filenames']:
            only_filenames = []
            for string in conflict_files:
                only_filenames.append(string.rpartition('/')[2])

            show_files = only_filenames

        # Add an "Open all ..." option
        show_files.insert(0, messages['open_all'])

        # Show the conflict files in the quickpanel and open them on selection
        def open_conflict(index):
            if index < 0:
                return
            elif index == 0:
                # Open all ...
                for file in conflict_files:
                    window.open_file(file)
            else:
                window.open_file(
                    os.path.join(git_repo, conflict_files[index - 1])
                )

        window.show_quick_panel(show_files, open_conflict)

    def _get_conflict_files(self, working_dir):
        # Search for conflicts using git executable
        return execute_command([
            settings['git_path'],
            "diff", "--name-only",
            "--diff-filter=U"
            ],
            working_dir=working_dir
        )

    def _determine_git_dir(self):
        open_view_path = self.window.active_view().file_name()
        open_folders = self.window.folders()

        working_dir = None
        if open_view_path:
            # Remove the traling filename, we just need the folder
            working_dir = re.sub(r"[/\\][^\\/]*$",
                                 "",
                                 open_view_path)
        elif open_folders:
            working_dir = open_folders[0]

        # Get git top-level folder
        if working_dir:
            working_dir = execute_command([
                settings['git_path'],
                "rev-parse", "--show-toplevel"
                ],
                working_dir=working_dir)

        return working_dir


def execute_command(command, working_dir=None):
    startupinfo = None
    # hide console window on windows
    if os.name == 'nt':
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW

    output = None
    try:
        output = subprocess.check_output(
            command,
            cwd=working_dir,
            startupinfo=startupinfo
        )
    except (subprocess.CalledProcessError, AttributeError):
        # Git will return an error when the given directory
        # is not a repository, which means that we can ignore this error
        pass
    else:
        output = str(output, encoding="utf-8").strip()

    return output


class ScanForConflicts(sublime_plugin.EventListener):
    def on_activated(self, view):
        if settings['live_matching']:
            highlight_conflicts(view)

    def on_load(self, view):
        if settings['live_matching']:
            highlight_conflicts(view)

    def on_pre_save(self, view):
        if settings['live_matching']:
            highlight_conflicts(view)


# ST3 automatically calls plugin_loaded when the API is ready
# For ST2 we have to call the function manually
if not int(sublime.version()) > 3000:
    plugin_loaded()
