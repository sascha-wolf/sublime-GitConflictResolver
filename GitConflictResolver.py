import sublime_plugin, sublime
import re

sentinel = object()

CONFLICT_PATTERN = re.compile(r'<<<<<<<[^\n]*\n((?s).*?)=======\n((?s).*?)>>>>>>>[^\n]*\n')

messages = {
    "no_conflict_found": "No conflict found"
}


def findConflict(view, begin=sentinel):
    if begin is sentinel:
        if len(view.sel()) == 0:
            begin = 0
        else:
            begin = view.sel()[0].begin()

    conflict_region = view.find(CONFLICT_PATTERN.pattern, begin)

    if not conflict_region:
        conflict_region = view.find(CONFLICT_PATTERN.pattern, begin)
        if not conflict_region:
            sublime.status_message(messages['no_conflict_found'])
            return None

    return conflict_region


def keep(view, region, old):
    if old:
        keep_type = r'\1'
    else:
        keep_type = r'\2'

    conflict_text = view.substr(region)
    return CONFLICT_PATTERN.sub(keep_type, conflict_text)


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
        conflict_region = findConflict(self.view)

        if conflict_region is None:
            return

        replace_text = keep(self.view, conflict_region, old=False)
        self.view.replace(edit, conflict_region, replace_text)


class KeepOld(sublime_plugin.TextCommand):
    def run(self, edit):
        conflict_region = findConflict(self.view)

        if conflict_region is None:
            return

        replace_text = keep(self.view, conflict_region, old=True)
        self.view.replace(edit, conflict_region, replace_text)
