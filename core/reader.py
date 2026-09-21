"""Device-independent reading state and local persistence."""
from dataclasses import asdict, dataclass, replace
import hashlib
import json
import os
from pathlib import Path
import re
import tempfile


@dataclass(frozen=True)
class ReaderState:
    reading_enabled: bool = False
    document_id: str = ""
    group_index: int = 0
    group_offset: int = 0
    display_mode: str = "Normal"
    opacity: float = 0.9
    hide_key: int = 0
    panel_width: int = 640
    panel_height: int = 0  # Zero keeps automatic height.
    transparent_background: bool = False
    font_color: str = "#f3f5f7"
    font_size: int = 0  # Zero keeps the display-mode default.


class ReaderStore:
    """Never reads or writes mouse profiles/config.json."""

    def __init__(self, directory):
        self.directory = Path(directory)

    def _write(self, path, value):
        path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
        fd, temporary = tempfile.mkstemp(dir=path.parent, suffix=".tmp")
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as stream:
                json.dump(value, stream, ensure_ascii=False)
                stream.flush()
                os.fsync(stream.fileno())
            os.replace(temporary, path)
        finally:
            if os.path.exists(temporary):
                os.unlink(temporary)

    def load_state(self):
        path = self.directory / "state.json"
        if not path.exists():
            return ReaderState()
        state = ReaderState(**json.loads(path.read_text(encoding="utf-8")))
        if (type(state.reading_enabled) is not bool
                or not isinstance(state.document_id, str)
                or (state.document_id and not re.fullmatch(r"[0-9a-f]{64}", state.document_id))
                or type(state.group_index) is not int or state.group_index < 0
                or type(state.group_offset) is not int or state.group_offset < 0
                or state.display_mode not in ("Normal", "Minimal", "Ghost")
                or type(state.opacity) not in (int, float) or not 0.2 <= state.opacity <= 1
                or type(state.hide_key) is not int or not 0 <= state.hide_key <= 255
                or type(state.panel_width) is not int or not 240 <= state.panel_width <= 1920
                or type(state.panel_height) is not int
                or not (state.panel_height == 0 or 80 <= state.panel_height <= 1080)
                or type(state.transparent_background) is not bool
                or not isinstance(state.font_color, str)
                or not re.fullmatch(r"#[0-9a-fA-F]{6}", state.font_color)
                or type(state.font_size) is not int
                or not (state.font_size == 0 or 12 <= state.font_size <= 72)):
            raise ValueError("Invalid reader state; existing file has been preserved")
        return state

    def save_state(self, state):
        self._write(self.directory / "state.json", asdict(state))

    def save_document(self, title, groups):
        if not groups or any(not isinstance(g, str) or not g.strip() for g in groups):
            raise ValueError("The document contains no readable text")
        document = {"title": title, "groups": list(groups), "grouping_version": 2}
        payload = json.dumps(document, ensure_ascii=False).encode("utf-8")
        document_id = hashlib.sha256(payload).hexdigest()
        self._write(self.directory / "documents" / (document_id + ".json"), document)
        return document_id

    def load_document(self, document_id):
        if not re.fullmatch(r"[0-9a-f]{64}", document_id):
            raise ValueError("Invalid reader document reference")
        document = json.loads((self.directory / "documents" / (document_id + ".json")).read_text(encoding="utf-8"))
        if (not isinstance(document.get("title"), str)
                or not isinstance(document.get("groups"), list)
                or not document["groups"]
                or any(not isinstance(g, str) or not g.strip() for g in document["groups"])):
            raise ValueError("Invalid reader document")
        return document


class ReaderModel:
    """Owned by the UI thread; temporary visibility is never persisted."""

    def __init__(self, store):
        self.store = store
        self.state = store.load_state()
        self.document = store.load_document(self.state.document_id) if self.state.document_id else None
        self.hidden = False
        if self.document:
            self.state = replace(self.state, group_index=min(self.state.group_index, len(self.groups) - 1))
            if self.document.get("grouping_version", 1) < 2:
                self._regroup_legacy_document()
        elif self.state.reading_enabled:
            self.state = replace(self.state, reading_enabled=False)

    def _regroup_legacy_document(self):
        from core.reader_import import group_sentences
        # Match by text offset, not the old page number; keep the old document file.
        offset = sum(len(re.sub(r"\s", "", group))
                     for group in self.groups[:self.state.group_index])
        groups = group_sentences(" ".join(self.groups))
        index, consumed = 0, 0
        for index, group in enumerate(groups):
            consumed += len(re.sub(r"\s", "", group))
            if consumed > offset:
                break
        document_id = self.store.save_document(self.document["title"], groups)
        document = self.store.load_document(document_id)
        state = replace(self.state, document_id=document_id, group_index=index)
        self.store.save_state(state)
        self.document, self.state = document, state

    @property
    def groups(self):
        return self.document["groups"] if self.document else []

    @property
    def text(self):
        return self.groups[self.state.group_index] if self.groups else ""

    @property
    def visible(self):
        return self.state.reading_enabled and bool(self.groups) and not self.hidden

    def update(self, **changes):
        state = replace(self.state, **changes)
        if state.reading_enabled and not self.groups:
            raise ValueError("Import a document before enabling Reading Mode")
        self.store.save_state(state)
        self.state = state

    def open_document(self, title, groups):
        document_id = self.store.save_document(title, groups)
        document = self.store.load_document(document_id)
        state = replace(self.state, document_id=document_id, group_index=0, group_offset=0)
        self.store.save_state(state)
        self.document, self.state = document, state

    def navigate(self, direction):
        if not self.state.reading_enabled or not self.groups:
            return
        index = max(0, min(len(self.groups) - 1, self.state.group_index + direction))
        if index != self.state.group_index:
            self.update(group_index=index, group_offset=0)

    def set_hidden(self, hidden):
        self.hidden = bool(hidden)

