import sublime_plugin, sublime
import re

sentinel = object()

# view.find sadly can't handle naming groups
NO_NAMING_GROUPS_PATTERN = "(?s)<{7}[^\n]*\n(.*?)(?:\|{7}[^\n]*\n(.*?))?={7}\n(.*?)>{7}[^\n]*\n"
CONFLICT_REGEX = re.compile(r"(?s)<{7}[^\n]*\n(?P<old>.*?)(?:\|{7}[^\n]*\n(?P<ancestor>.*?))?={7}\n(?P<new>.*?)>{7}[^\n]*\n")
OLD = 'old'
NEW = 'new'
ANCESTOR = 'ancestor'

messages = {
    "no_conflict_found": "No conflict found",
    "no_such_group": "No such conflict group found"
}


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


def keep(view, region, keep_type):
    conflict_text = view.substr(region)
    match = CONFLICT_REGEX.search(conflict_text)

    # If we didn't matched the group return None
    if not match.group(keep_type):
        sublime.status_message(messages['no_such_group'])
        return None

    return CONFLICT_REGEX.sub(r'\g<'+keep_type+'>', conflict_text)


def resolveConflict(view, edit, keep_type):
    conflict_region = findConflict(view)

    if conflict_region is None:
        return

    replace_text = keep(view, conflict_region, NEW)

    if not replace_text:
        return

    view.replace(edit, conflict_region, replace_text)


class FindNextConflict(sublime_plugin.TextCommand):
    def run(self, edit):
        conflict_region = findConflict(self.view)
        if conflict_region is None:
            return

        # Add the region to the selection
        self.view.show(conflict_region)
        self.view.sel().clear()
        self.view.sel().add(conflict_region)


class KeepNew(sublime_plugin.TextCommand):
    def run(self, edit):
        resolveConflict(self.view, edit, NEW)


class KeepOld(sublime_plugin.TextCommand):
    def run(self, edit):
        resolveConflict(self.view, edit, OLD)


class KeepCommonAncestor(sublime_plugin.TextCommand):
    def run(self, edit):
        resolveConflict(self.view, edit, ANCESTOR)
