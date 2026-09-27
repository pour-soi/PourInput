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
        self.anchors = {}
        self.headings = []
        self.heading_start = None

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if not self.skip and (attrs.get("id") or attrs.get("name")):
            self.anchors[attrs.get("id") or attrs["name"]] = sum(map(len, self.parts))
        if tag in ("head", "script", "style"):
            self.skip += 1
        if not self.skip and tag in ("p", "div", "br", "li", "h1", "h2", "h3"):
            self.parts.append("\n")
        if not self.skip and tag in ("h1", "h2", "h3"):
            self.heading_start = sum(map(len, self.parts))

    def handle_endtag(self, tag):
        if tag in ("h1", "h2", "h3") and self.heading_start is not None:
            title = "".join(self.parts)[self.heading_start:].strip()
            if title:
                self.headings.append((title, self.heading_start))
            self.heading_start = None
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


def _epub_text(path, with_chapters=False):
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
        parts, locations, entries, fallback = [], {}, [], []
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
            start = sum(map(len, parts)) + 2 * len(parts)
            locations[name] = start
            for fragment, offset in parser.anchors.items():
                locations[name + "#" + fragment] = start + offset
            fallback.extend((title, start + offset) for title, offset in parser.headings)
            parts.append("".join(parser.parts))
        text = "\n\n".join(parts)
        if not with_chapters:
            return text
        # EPUB 3 navigation and EPUB 2 NCX point to exact spine anchors.
        for item in manifest.values():
            is_nav = "nav" in item.get("properties", "").split()
            is_ncx = item.get("media-type") == "application/x-dtbncx+xml"
            if not (is_nav or is_ncx):
                continue
            name = _epub_member(posixpath.dirname(package_name), item.attrib["href"])
            root = ET.fromstring(read(name))
            nodes = []
            if is_nav:
                for nav in root.iter():
                    if nav.tag.split("}")[-1] == "nav" and "toc" in nav.get("{http://www.idpf.org/2007/ops}type", "").split():
                        nodes.extend(("".join(a.itertext()).strip(), a.get("href", ""))
                                     for a in nav.iter() if a.tag.split("}")[-1] == "a")
            else:
                for point in root.iter():
                    if point.tag.split("}")[-1] == "navPoint":
                        label = next((n for n in point if n.tag.split("}")[-1] == "navLabel"), None)
                        content = next((n for n in point if n.tag.split("}")[-1] == "content"), None)
                        if label is not None and content is not None:
                            nodes.append(("".join(label.itertext()).strip(), content.get("src", "")))
            for title, href in nodes:
                if not title or not href:
                    continue
                target = _epub_member(posixpath.dirname(name), href)
                fragment = unquote(urlsplit(href).fragment)
                key = target + ("#" + fragment if fragment else "")
                if key in locations:
                    entries.append((title, locations[key]))
            if entries:
                break
        from core.reader_chapters import headings
        return text, entries or fallback or headings(text)


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


def import_document(path, with_chapters=False):
    from core.reader_chapters import headings, anchors, inferred_headings
    entries = []
    path = Path(path)
    if path.stat().st_size > MAX_IMPORT_BYTES:
        raise ValueError("Choose a TXT or EPUB file smaller than 32 MB")
    suffix = path.suffix.lower()
    if suffix == ".txt":
        text = _decode_text(path.read_bytes())
        entries = headings(text)
    elif suffix == ".epub":
        if with_chapters:
            text, entries = _epub_text(path, True)
        else:
            text = _epub_text(path)
    else:
        raise ValueError("Only TXT and EPUB files are supported")
    groups = group_sentences(text)
    if not groups:
        raise ValueError("The document contains no readable text")
    if with_chapters:
        inferred = not entries
        if inferred:
            entries = inferred_headings(text)
        chapters = anchors(text, entries, groups)
        if inferred:
            for chapter in chapters:
                chapter['inferred'] = True
        return path.stem, groups, chapters
    return path.stem, groups

