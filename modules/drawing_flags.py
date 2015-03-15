import sublime

from . import settings


_st_version = int(sublime.version())


def visible():
    fill = settings.get('fill_conflict_area')
    outline = settings.get('outline_conflict_area')

    flags = 0
    if _st_version < 3000:
        # If fill is set then outline is ignored; ST2 doesn't provide a combination
        if not (fill or outline):
            flags = sublime.HIDDEN
        elif not fill and outline:
            flags = sublime.DRAW_OUTLINED
    else:
        if not fill:
            flags |= sublime.DRAW_NO_FILL
        if not outline:
            flags |= sublime.DRAW_NO_OUTLINE

    return flags


def hidden():
    flags = 0
    if _st_version < 3000:
        flags = sublime.HIDDEN
    else:
        flags = (sublime.DRAW_NO_FILL |
                 sublime.DRAW_NO_OUTLINE)

    return (flags | sublime.HIDE_ON_MINIMAP)
