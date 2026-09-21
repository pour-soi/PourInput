"""Local TXT/EPUB extraction and deterministic, bounded sentence grouping."""
from html.parser import HTMLParser
from pathlib import Path
import posixpath
import re
from urllib.parse import unquote, urlsplit
import xml.etree.ElementTree as ET
import zipfile

MAX_IMPORT_BYTES = 32 * 1024 * 1024
MAX_EPUB_TEXT_BYTES = 64 * 1024 * 1024


class _TextParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.parts = []
        self.skip = 0

    def handle_starttag(self, tag, attrs):
        if tag in ("head", "script", "style"):
            self.skip += 1
        if not self.skip and tag in ("p", "div", "br", "li", "h1", "h2", "h3"):
            self.parts.append("\n")

    def handle_endtag(self, tag):
        if tag in ("head", "script", "style"):
            self.skip = max(0, self.skip - 1)
        if not self.skip and tag in ("p", "div", "li", "h1", "h2", "h3"):
            self.parts.append("\n")

    def handle_data(self, data):
        if not self.skip:
            self.parts.append(data)


def _decode_text(data):
    if data.startswith((b"\xff\xfe", b"\xfe\xff")):
        return data.decode("utf-16")
    try:
        return data.decode("utf-8-sig")
    except UnicodeDecodeError:
        return data.decode("gb18030")


def _epub_member(base, href):
    parsed = urlsplit(href)
    if parsed.scheme or parsed.netloc:
        raise ValueError("EPUB must reference local chapters")
    name = posixpath.normpath(posixpath.join(base, unquote(parsed.path)))
    if name.startswith(("/", "../")) or name == ".." or "\\" in name:
        raise ValueError("Invalid EPUB chapter path")
    return name


def _epub_text(path):
    with zipfile.ZipFile(path) as archive:
        total = 0

        def read(name):
            nonlocal total
            info = archive.getinfo(name)
            total += info.file_size
            if total > MAX_EPUB_TEXT_BYTES:
                raise ValueError("EPUB text is too large")
            return archive.read(info)

        container = ET.fromstring(read("META-INF/container.xml"))
        rootfile = next((node for node in container.iter() if node.tag.split("}")[-1] == "rootfile"), None)
        if rootfile is None:
            raise ValueError("EPUB has no package document")
        package_name = _epub_member("", rootfile.attrib["full-path"])
        package = ET.fromstring(read(package_name))
        manifest = {node.attrib["id"]: node for node in package.iter()
                    if node.tag.split("}")[-1] == "item"}
        parts = []
        for itemref in package.iter():
            if itemref.tag.split("}")[-1] != "itemref" or itemref.get("linear") == "no":
                continue
            item = manifest[itemref.attrib["idref"]]
            if item.get("media-type") not in ("application/xhtml+xml", "text/html"):
                continue
            name = _epub_member(posixpath.dirname(package_name), item.attrib["href"])
            data = read(name)
            # XML handles the chapter's declared encoding; HTML fallback is UTF-8.
            try:
                chapter = ET.fromstring(data)
                for node in chapter.iter():
                    node.tag = node.tag.split("}")[-1]
                markup = ET.tostring(chapter, encoding="unicode")
            except ET.ParseError:
                markup = data.decode("utf-8-sig")
            parser = _TextParser()
            parser.feed(markup)
            parts.append("".join(parser.parts))
        return "\n\n".join(parts)


def group_sentences(text, target_chars=120):
    """Balance text amounts, preferring nearby punctuation then word boundaries."""
    if target_chars < 40:
        raise ValueError("Invalid grouping target")
    text = re.sub(r"\s+", " ", text).strip()
    count = max(1, round(len(text) / target_chars))
    groups, start = [], 0
    while count > 1:
        size = (len(text) - start) / count
        ideal = start + round(size)
        margin = max(1, round(size * 0.15))
        low, high = ideal - margin, min(len(text) - 1, ideal + margin)
        punctuation, spaces = [], []
        for end in range(low, high + 1):
            previous = text[end - 1]
            if previous in "。！？!?，,；;：:、”’」』":
                punctuation.append(end)
            elif previous == "." and (end == len(text) or text[end].isspace()):
                punctuation.append(end)
            elif text[end].isspace():
                spaces.append(end)
        candidates = punctuation or spaces or [ideal]
        end = min(candidates, key=lambda point: (abs(point - ideal), point))
        groups.append(text[start:end].strip())
        start = end
        count -= 1
    if text[start:].strip():
        groups.append(text[start:].strip())
    return groups


def import_document(path):
    path = Path(path)
    if path.stat().st_size > MAX_IMPORT_BYTES:
        raise ValueError("Choose a TXT or EPUB file smaller than 32 MB")
    suffix = path.suffix.lower()
    if suffix == ".txt":
        text = _decode_text(path.read_bytes())
    elif suffix == ".epub":
        text = _epub_text(path)
    else:
        raise ValueError("Only TXT and EPUB files are supported")
    groups = group_sentences(text)
    if not groups:
        raise ValueError("The document contains no readable text")
    return path.stem, groups

