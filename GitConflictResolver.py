import sublime_plugin
import re

sentinel = object()

CONFLICT_PATTERN = re.compile(r'(?s)<<<<<<<[\w ]*(.*?)=======\n(.*?)>>>>>>>[\w ]*')


def findConflict(view, begin=sentinel):
    if begin is sentinel:
        if len(view.sel()) == 0:
            begin = 0
        else:
            begin = view.sel()[0].begin()

    return view.find(CONFLICT_PATTERN.pattern, begin)


def keep(view, region, theirs):
    if theirs:
        keep_type = r'\1'
    else:
        keep_type = r'\2'

    conflict_text = view.substr(region)
    return CONFLICT_PATTERN.sub(keep_type, conflict_text)


class FindNextConflict(sublime_plugin.TextCommand):

    def run(self, edit):
        conflict_region = findConflict(self.view)
        if conflict_region.empty() or conflict_region is None:
            return

        # Add the region to the selection
        self.view.show(conflict_region)
        self.view.sel().clear()
        self.view.sel().add(conflict_region)


class KeepMine(sublime_plugin.TextCommand):
    def run(self, edit):
        conflict_region = findConflict(self.view)

        replace_text = keep(self.view, conflict_region, theirs=False)
        self.view.replace(edit, conflict_region, replace_text)


class KeepTheirs(sublime_plugin.TextCommand):
    def run(self, edit):
        conflict_region = findConflict(self.view)

        replace_text = keep(self.view, conflict_region, theirs=True)
        self.view.replace(edit, conflict_region, replace_text)
