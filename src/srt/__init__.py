import re
from datetime import timedelta
from dataclasses import dataclass
from typing import Iterable, List

@dataclass
class Subtitle:
    index: int
    start: timedelta
    end: timedelta
    content: str

_TIME_PATTERN = re.compile(r"(\d{2}:\d{2}:\d{2},\d{3})\s-->\s(\d{2}:\d{2}:\d{2},\d{3})")


def _timedelta_to_str(td: timedelta) -> str:
    total_ms = int(td.total_seconds() * 1000)
    hours = total_ms // 3600000
    minutes = (total_ms % 3600000) // 60000
    seconds = (total_ms % 60000) // 1000
    milliseconds = total_ms % 1000
    return f"{hours:02}:{minutes:02}:{seconds:02},{milliseconds:03}"


def _str_to_timedelta(s: str) -> timedelta:
    h, m, rest = s.split(":")
    sec, ms = rest.split(",")
    return timedelta(hours=int(h), minutes=int(m), seconds=int(sec), milliseconds=int(ms))


def parse(data: str) -> Iterable[Subtitle]:
    blocks = []
    current = []
    for line in data.splitlines():
        if line.strip() == "":
            if current:
                blocks.append(current)
                current = []
        else:
            current.append(line)
    if current:
        blocks.append(current)

    subtitles: List[Subtitle] = []
    for block in blocks:
        idx_line = block[0].strip()
        try:
            index = int(idx_line)
            times_line = block[1].strip()
            content_lines = block[2:]
        except (ValueError, IndexError):
            continue
        m = _TIME_PATTERN.match(times_line)
        if not m:
            continue
        start = _str_to_timedelta(m.group(1))
        end = _str_to_timedelta(m.group(2))
        content = "\n".join(content_lines)
        subtitles.append(Subtitle(index=index, start=start, end=end, content=content))
    return subtitles


def compose(subs: Iterable[Subtitle]) -> str:
    lines = []
    for i, sub in enumerate(subs, start=1):
        idx = sub.index if sub.index is not None else i
        lines.append(str(idx))
        lines.append(f"{_timedelta_to_str(sub.start)} --> {_timedelta_to_str(sub.end)}")
        lines.extend(sub.content.splitlines())
        lines.append("")
    return "\n".join(lines)
