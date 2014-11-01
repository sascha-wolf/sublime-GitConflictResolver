import sublime
import sublime_plugin
import os

from .modules import conflict_re
from .modules import git_mixin
from .modules import messages as msgs
from .modules import settings

icons = {
    "ours": "Packages/Git Conflict Resolver/gutter/ours.png",
    "ancestor": "Packages/Git Conflict Resolver/gutter/ancestor.png",
    "theirs": "Packages/Git Conflict Resolver/gutter/theirs.png"
}


def plugin_loaded():
    settings.load()


def find_conflict(view, begin=0):
    conflict_region = view.find(conflict_re.NO_NAMING_GROUPS_PATTERN, begin)

    if not conflict_region:
        conflict_region = view.find(conflict_re.NO_NAMING_GROUPS_PATTERN, 0)
        if not conflict_region:
            sublime.status_message(msgs.get('no_conflict_found'))
            return None

    return conflict_region


def highlight_conflict_group(view, group):
    scope = group + '_gutter'
    if settings.get(scope):
        conflict_regions = view.find_all(conflict_re.CONFLICT_GROUP_REGEX[group])

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
    conflict_regions = view.find_all(conflict_re.NO_NAMING_GROUPS_PATTERN)

    view.erase_regions("GitConflictRegions")
    view.add_regions(
        "GitConflictRegions",
        conflict_regions,
        settings.get('matching_scope'),
        "",
        (0 if settings.get('fill_conflict_area') else sublime.DRAW_NO_FILL)
        |
        (0 if settings.get('outline_conflict_area') else sublime.DRAW_NO_OUTLINE)
    )

    highlight_conflict_group(view, 'ours')
    highlight_conflict_group(view, 'ancestor')
    highlight_conflict_group(view, 'theirs')


def extract(view, region, keep):
    conflict_text = view.substr(region)
    match = conflict_re.CONFLICT_REGEX.search(conflict_text)

    # If we didn't matched the group return None
    if not match.group(keep):
        sublime.status_message(msgs.get('no_such_group'))
        return None

    return conflict_re.CONFLICT_REGEX.sub(r'\g<' + keep + '>', conflict_text)


class FindNextConflict(sublime_plugin.TextCommand):
    def run(self, edit):
        # Reload settings
        settings.load()

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
        # Reload settings
        settings.load()

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


class ListConflictFiles(sublime_plugin.WindowCommand, git_mixin.GitMixin):
    def run(self):
        # Reload settings
        settings.load()

        # Ensure git executable is available
        if not self.git_executable_available():
            sublime.error_message(msgs.get('git_executable_not_found'))
            return

        self.git_repo = self.determine_git_repo()
        if not self.git_repo:
            sublime.status_message(msgs.get('no_git_repo_found'))
            return

        conflict_files = self.get_conflict_files()
        if not conflict_files:
            sublime.status_message(msgs.get('no_conflict_files_found', self.git_repo))
            return

        self.show_quickpanel_selection(conflict_files)

    def get_conflict_files(self):
        # Search for conflicts using git executable
        conflict_files = self.git_command(
            ["diff", "--name-only", "--diff-filter=U"],
            repo=self.git_repo
        )

        conflict_files = conflict_files.split('\n')
        # Remove empty strings and sort the list
        # (TODO: sort also filenames only?)
        return sorted([x for x in conflict_files if x])

    def get_representation_list(self, conflict_files):
        """Returns a list with only filenames if the 'show_only_filenames'
        option is set, otherwise it returns just a clone of the given list"""
        result = None
        if settings.get('show_only_filenames'):
            result = []
            for string in conflict_files:
                result.append(string.rpartition('/')[2])
        else:
            result = list(conflict_files)

        # Add an "Open all ..." option
        result.insert(0, msgs.get('open_all'))

        return result

    def show_quickpanel_selection(self, conflict_files):
        full_path = [os.path.join(self.git_repo, x) for x in conflict_files]
        show_files = self.get_representation_list(conflict_files)

        # Show the conflict files in the quickpanel and open them on selection
        def open_conflict(index):
            if index < 0:
                return
            elif index == 0:
                # Open all ...
                self.open_files(*full_path)
            else:
                self.open_files(full_path[index - 1])

        self.window.show_quick_panel(show_files, open_conflict)

    def open_files(self, *files):
        for file in files:
            # Workaround sublime issue #39 using sublime.set_timeout
            # (open_file() does not set cursor when run from a quick panel callback)
            sublime.set_timeout(
                lambda file=file: init_view(self.window.open_file(file)),
                0
            )


def init_view(view):
    return  # TODO: Find a workaround for the cursor position bug

    if view.is_loading():
        sublime.set_timeout(lambda: init_view(view), 50)
    else:
        view.run_command("find_next_conflict")


class ScanForConflicts(sublime_plugin.EventListener):
    def on_activated(self, view):
        if settings.get('live_matching'):
            highlight_conflicts(view)

    def on_load(self, view):
        if settings.get('live_matching'):
            highlight_conflicts(view)

    def on_pre_save(self, view):
        if settings.get('live_matching'):
            highlight_conflicts(view)


# ST3 automatically calls plugin_loaded when the API is ready
# For ST2 we have to call the function manually
if not int(sublime.version()) > 3000:
    plugin_loaded()
