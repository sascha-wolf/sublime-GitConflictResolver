import re

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
