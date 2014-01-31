import sublime_plugin, sublime
import re

sentinel = object()

# view.find sadly can't handle naming groups
NO_NAMING_GROUPS_PATTERN = "(?s)<{7}[^\n]*\n(.*?)(?:\|{7}[^\n]*\n(.*?))?={7}\n(.*?)>{7}[^\n]*\n"
CONFLICT_REGEX = re.compile(r"(?s)<{7}[^\n]*\n(?P<ours>.*?)(?:\|{7}[^\n]*\n(?P<ancestor>.*?))?={7}\n(?P<theirs>.*?)>{7}[^\n]*\n")

messages = {
    "no_conflict_found": "No conflict found",
    "no_such_group": "No such conflict group found"
}

# Global settings
settings_file = "GitConflictResolver.sublime-settings"


def plugin_loaded():
    global settings, live_matching, matching_scope
    global fill_conflict_area, outline_conflict_area

    settings = sublime.load_settings(settings_file)
    live_matching = bool(settings.get('live_matching', True))
    matching_scope = settings.get('matching_scope', 'invalid')
    fill_conflict_area = settings.get('fill_conflict_area', False)
    outline_conflict_area = settings.get('outline_conflict_area', True)


def findConflict(view, begin=sentinel):
    if begin is sentinel:
        if len(view.sel()) == 0:
            begin = 0
        else:
            begin = view.sel()[0].begin()

    conflict_region = view.find(NO_NAMING_GROUPS_PATTERN, begin)

    if not conflict_region:
        conflict_region = view.find(NO_NAMING_GROUPS_PATTERN, 0)
        if not conflict_region:
            sublime.status_message(messages['no_conflict_found'])
            return None

    return conflict_region


def highlightConflicts(view):
    conflict_regions = view.find_all(NO_NAMING_GROUPS_PATTERN)

    view.erase_regions("GitConflictRegions")
    view.add_regions("GitConflictRegions",
        conflict_regions,
        matching_scope,
        "",
        (0 if fill_conflict_area else sublime.DRAW_NO_FILL)
        |
        (0 if outline_conflict_area else sublime.DRAW_NO_OUTLINE)
        )


def extract(view, region, keep):
    conflict_text = view.substr(region)
    match = CONFLICT_REGEX.search(conflict_text)

    # If we didn't matched the group return None
    if not match.group(keep):
        sublime.status_message(messages['no_such_group'])
        return None

    return CONFLICT_REGEX.sub(r'\g<'+keep+'>', conflict_text)


class FindNextConflict(sublime_plugin.TextCommand):
    def run(self, edit):
        conflict_region = findConflict(self.view)
        if conflict_region is None:
            return

        # Add the region to the selection
        self.view.show_at_center(conflict_region)
        self.view.sel().clear()
        self.view.sel().add(conflict_region)


class Keep(sublime_plugin.TextCommand):
    def run(self, edit, keep):
        conflict_region = findConflict(self.view)

        if conflict_region is None:
            return

        replace_text = extract(self.view, conflict_region, keep)

        if not replace_text:
            return

        self.view.replace(edit, conflict_region, replace_text)


class ScanForConflicts(sublime_plugin.EventListener):
    def on_activated(self, view):
        if(live_matching):
            highlightConflicts(view)

    def on_pre_save(self, view):
        if(live_matching):
            highlightConflicts(view)


# ST3 automatically calls plugin_loaded when the API is ready
# For ST2 we have to call the function manually
if not int(sublime.version()) > 3000:
    plugin_loaded()