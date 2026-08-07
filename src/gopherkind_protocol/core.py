"""Independent implementation of the Gopherkind kind 31436 grammar."""

from __future__ import annotations

from dataclasses import dataclass
import re
from typing import Any, Iterable
from urllib.parse import quote

DOC_KIND = 31436
_ASCII_DECIMAL = re.compile(r"^[0-9]+$")


@dataclass(frozen=True)
class Document:
    path: str
    type: str
    title: str


@dataclass(frozen=True)
class KindmapLine:
    type: str
    display: str
    link: str | None = None

    def as_fixture_value(self) -> dict[str, str]:
        value = {"type": self.type, "display": self.display}
        if self.link is not None:
            value["link"] = self.link
        return value


def _has_control(value: str) -> bool:
    return any(ord(char) <= 0x1F or 0x7F <= ord(char) <= 0x9F for char in value)


def _well_formed(value: str) -> bool:
    return not any(0xD800 <= ord(char) <= 0xDFFF for char in value)


# SPEC.md: display text may carry SGR ("ESC [", zero or more of "0123456789;:",
# then "m"). Those are colour and style only. Everything else that is a control
# character becomes a space; the sequence is not removed, each character in it
# is replaced.
_SGR = re.compile("\x1b\\[[0-9;:]*m")


def _clean(value: str) -> str:
    """Replace every control character with a space (no SGR exemption)."""
    return "".join(" " if ord(char) <= 0x1F or 0x7F <= ord(char) <= 0x9F else char for char in value)


def _has_non_sgr_control(value: str) -> bool:
    return _has_control(_SGR.sub("", value))


def _clean_display(value: str) -> str:
    """Keep SGR sequences, space out every other control character."""
    out: list[str] = []
    index = 0
    for match in _SGR.finditer(value):
        out.append(_clean(value[index : match.start()]))
        out.append(match.group(0))
        index = match.end()
    out.append(_clean(value[index:]))
    return "".join(out)


def valid_path(value: object) -> bool:
    if not isinstance(value, str) or not _well_formed(value) or _has_control(value):
        return False
    if value == "/":
        return True
    if not value.startswith("/") or value.endswith("/"):
        return False
    return all(segment not in ("", ".", "..") for segment in value[1:].split("/"))


def url_path(value: str) -> str:
    """Encode each exact path segment once without normalising it."""
    return "/".join(quote(segment, safe="") for segment in value.split("/"))


def _named_tags(event: dict[str, Any], name: str) -> list[list[Any]]:
    tags = event.get("tags")
    if not isinstance(tags, list):
        return []
    return [tag for tag in tags if isinstance(tag, list) and tag and tag[0] == name]


def parse_document(event: dict[str, Any]) -> Document | None:
    if event.get("kind") != DOC_KIND:
        return None
    paths = _named_tags(event, "d")
    types = _named_tags(event, "type")
    titles = _named_tags(event, "title")
    if len(paths) != 1 or len(types) != 1 or len(titles) > 1:
        return None
    path = paths[0][1] if len(paths[0]) > 1 else None
    item_type = types[0][1] if len(types[0]) > 1 else None
    title = titles[0][1] if titles and len(titles[0]) > 1 else path
    if not valid_path(path) or item_type not in ("0", "1"):
        return None
    if not isinstance(title, str) or not _well_formed(title) or _has_control(title):
        return None
    return Document(path=path, type=item_type, title=title)


def parse_kindmap(content: str) -> list[KindmapLine]:
    records = content.split("\n")
    if records and records[-1] == "":
        records.pop()
    output: list[KindmapLine] = []
    for raw in records:
        record = raw[:-1] if raw.endswith("\r") else raw
        if "\t" not in record:
            display = record[1:] if record.startswith("i") else record
            output.append(KindmapLine("i", _clean_display(display)))
            continue
        heading, link, *_ignored = record.split("\t")
        item_type = heading[0] if heading else ""
        display = heading[1:] if heading else ""
        printable_type = len(item_type) == 1 and 0x21 <= ord(item_type) <= 0x7E
        if (
            not printable_type
            or item_type == "i"
            or link == ""
            or _has_non_sgr_control(display)
            or _has_control(link)
        ):
            output.append(KindmapLine("i", _clean_display(display)))
        else:
            output.append(KindmapLine(item_type, _clean_display(display), link))
    return output


def replacement_winner(events: Iterable[dict[str, Any]]) -> dict[str, Any] | None:
    winner: dict[str, Any] | None = None
    for event in events:
        if winner is None:
            winner = event
            continue
        candidate_key = (event.get("created_at", 0), _reverse_id(str(event.get("id", ""))))
        winner_key = (winner.get("created_at", 0), _reverse_id(str(winner.get("id", ""))))
        if candidate_key > winner_key:
            winner = event
    return winner


def _reverse_id(event_id: str) -> tuple[int, ...]:
    """Make lexicographically lower ids sort after higher ids in max()."""
    return tuple(-ord(char) for char in event_id)


def current_document(events: Iterable[dict[str, Any]], now: int) -> dict[str, Any] | None:
    winner = replacement_winner(events)
    if winner is None or parse_document(winner) is None:
        return None
    expirations = _named_tags(winner, "expiration")
    if expirations and len(expirations[0]) > 1:
        raw = expirations[0][1]
        if isinstance(raw, str) and _ASCII_DECIMAL.fullmatch(raw) and int(raw) <= now:
            return None
    return winner


def render_type0(content: str) -> str:
    lines = re.split(r"\r?\n", content)
    while lines and lines[-1] == "":
        lines.pop()
    stuffed = [f".{line}" if line.startswith(".") else line for line in lines]
    return "\r\n".join(stuffed) + "\r\n.\r\n"
