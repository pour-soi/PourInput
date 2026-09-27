"""Chapter recognition and stable anchors into stored reader groups."""
import re
from bisect import bisect_right

HEADING = r"(?:第[零〇一二三四五六七八九十百千万两\d]+[章回节卷部篇]|(?:chapter|part|book)\s+(?:\d+|[ivxlcdm]+)\b|序章|序言|楔子|尾声|后记)"


def headings(text, legacy=False):
    pattern = (r"(?<!\S)(" + HEADING + r")") if legacy else (r"^[ \t]*(" + HEADING + r")[^\n]{0,80}$")
    return [(match.group().strip(), match.start() + len(match.group()) - len(match.group().lstrip()))
            for match in re.finditer(pattern, text, re.I | re.M)]


def inferred_headings(text):
    """Conservative layout heuristic; never infer from flattened legacy text."""
    lines = text.splitlines(keepends=True)
    candidates, offset = [], 0
    for index, line in enumerate(lines):
        title = line.strip()
        isolated = (index == 0 or not lines[index - 1].strip()) and (
            index + 1 < len(lines) and not lines[index + 1].strip())
        if (isolated and 2 <= len(title) <= 30
                and not re.search(r'[。！？!?，,；;：:.“”「」<>＝=*_—–]', title)
                and not title.isdecimal()):
            # Poetry, lists and short fragments are not sufficient evidence.
            following = index + 1
            while following < len(lines) and not lines[following].strip():
                following += 1
            if following < len(lines) and len(lines[following].strip()) >= 50:
                candidates.append((title, offset + len(line) - len(line.lstrip())))
        offset += len(line)
    return candidates if len(candidates) >= 2 else []


def anchors(text, entries, groups):
    # Grouping normalizes whitespace; non-whitespace offsets remain stable.
    starts, count = [], 0
    for group in groups:
        starts.append(count)
        count += sum(not char.isspace() for char in group)
    result, seen = [], set()
    previous_offset, absolute = 0, 0
    for title, offset in sorted(entries, key=lambda entry: entry[1]):
        absolute += sum(not char.isspace() for char in text[previous_offset:offset])
        previous_offset = offset
        if absolute >= count or absolute in seen:
            continue
        seen.add(absolute)
        index = max(0, bisect_right(starts, absolute) - 1)
        chars = [i for i, char in enumerate(groups[index]) if not char.isspace()]
        result.append(dict(title=title, group_index=index,
                           group_offset=chars[absolute - starts[index]]))
    return sorted(result, key=lambda entry: (entry['group_index'], entry['group_offset']))


def legacy_chapters(groups):
    text = ' '.join(groups)
    return anchors(text, headings(text, legacy=True), groups)


def validate_chapters(chapters, groups):
    if not isinstance(chapters, list):
        raise ValueError("Invalid reader chapters")
    previous = (-1, -1)
    for entry in chapters:
        if not isinstance(entry, dict) or not isinstance(entry.get('title'), str) or not entry['title'].strip():
            raise ValueError("Invalid chapter title")
        if type(entry.get('inferred', False)) is not bool:
            raise ValueError("Invalid chapter inference flag")
        index, offset = entry.get('group_index'), entry.get('group_offset')
        if (type(index) is not int or type(offset) is not int
                or not 0 <= index < len(groups) or not 0 <= offset < len(groups[index])
                or (index, offset) <= previous):
            raise ValueError("Invalid chapter position")
        previous = index, offset
