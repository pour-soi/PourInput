import tempfile
import unittest
from unittest.mock import patch

from core.reader import ReaderModel, ReaderStore


class ReaderStateTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.store = ReaderStore(temporary.name)
        self.model = ReaderModel(self.store)

    def test_restart_restores_position_with_content_outside_state(self):
        self.model.open_document("Book", ["One.", "Two."])
        self.model.update(reading_enabled=True)
        self.model.navigate(1)
        restored = ReaderModel(self.store)
        self.assertEqual(restored.text, "Two.")
        self.assertTrue(restored.state.reading_enabled)
        state = (self.store.directory / "state.json").read_text()
        self.assertNotIn("Two.", state)
        self.assertFalse((self.store.directory / "config.json").exists())

    def test_hide_never_changes_or_saves_state(self):
        self.model.open_document("Book", ["One.", "Two."])
        self.model.update(reading_enabled=True)
        before = self.model.state
        with patch.object(self.store, "save_state") as save:
            self.model.set_hidden(True)
            self.assertFalse(self.model.visible)
            self.assertEqual(self.model.state, before)
            self.model.set_hidden(False)
            self.assertTrue(self.model.visible)
            save.assert_not_called()

    def test_navigation_clamps_and_disabled_mode_does_not_move(self):
        self.model.open_document("Book", ["One.", "Two."])
        self.model.navigate(1)
        self.assertEqual(self.model.state.group_index, 0)
        self.model.update(reading_enabled=True)
        self.model.navigate(-1)
        self.assertEqual(self.model.state.group_index, 0)
        self.model.navigate(99)
        self.assertEqual(self.model.state.group_index, 1)

    def test_failed_save_preserves_state(self):
        before = self.model.state
        with patch.object(self.store, "save_state", side_effect=OSError("disk full")):
            with self.assertRaises(OSError):
                self.model.update(display_mode="Ghost")
        self.assertEqual(self.model.state, before)

    def test_corrupt_state_preserved_and_reported(self):
        path = self.store.directory / "state.json"
        path.write_text('{"document_id": "../outside"}', encoding="utf-8")
        before = path.read_bytes()
        with self.assertRaises(ValueError):
            ReaderModel(self.store)
        self.assertEqual(path.read_bytes(), before)

    def test_old_reader_state_loads_default_panel_size(self):
        path = self.store.directory / "state.json"
        path.write_text('{"group_index": 0, "display_mode": "Ghost"}', encoding="utf-8")
        restored = ReaderModel(self.store)
        self.assertEqual(restored.state.panel_width, 640)
        self.assertEqual(restored.state.panel_height, 0)
        self.assertEqual(restored.state.display_mode, "Ghost")

    def test_panel_size_persists_without_changing_book_position(self):
        self.model.open_document("Book", ["One.", "Two."])
        self.model.update(reading_enabled=True)
        self.model.navigate(1)
        document = self.model.state.document_id
        self.model.update(panel_width=900, panel_height=280)
        restored = ReaderModel(self.store)
        self.assertEqual((restored.state.panel_width, restored.state.panel_height), (900, 280))
        self.assertEqual(restored.state.document_id, document)
        self.assertEqual(restored.state.group_index, 1)
        self.assertTrue(restored.state.reading_enabled)

    def test_panel_style_persists_with_book_state(self):
        self.model.open_document("Book", ["One.", "Two."])
        self.model.update(reading_enabled=True, group_index=1,
                          transparent_background=True, font_color="#12abef", font_size=32)
        restored = ReaderModel(self.store)
        self.assertEqual(restored.state, self.model.state)
        self.assertEqual(restored.text, "Two.")

    def test_legacy_state_defaults_to_visible_background_and_mode_font(self):
        (self.store.directory / "state.json").write_text('{}', encoding="utf-8")
        state = self.store.load_state()
        self.assertFalse(state.transparent_background)
        self.assertEqual(state.font_size, 0)
        self.assertEqual(state.font_color, "#f3f5f7")

    def test_empty_import_preserves_current_document(self):
        self.model.open_document("Book", ["One."])
        with self.assertRaises(ValueError):
            self.model.open_document("Empty", [])
        self.assertEqual(self.model.text, "One.")


    def test_legacy_regroup_preserves_text_position_settings_and_original(self):
        import json, re
        from dataclasses import replace
        groups = ["甲" * 40, "乙" * 180, "丙" * 25, "丁" * 160]
        old_id = self.store.save_document("Book", groups)
        path = self.store.directory / "documents" / (old_id + ".json")
        legacy = json.loads(path.read_text(encoding="utf-8"))
        legacy.pop("grouping_version")
        path.write_text(json.dumps(legacy, ensure_ascii=False), encoding="utf-8")
        original = path.read_bytes()
        old_state = replace(self.model.state, document_id=old_id, group_index=2,
                            reading_enabled=True, display_mode="Ghost", panel_width=400)
        self.store.save_state(old_state)
        restored = ReaderModel(self.store)
        self.assertEqual(path.read_bytes(), original)
        self.assertEqual(replace(restored.state, document_id=old_id, group_index=2), old_state)
        strip = lambda t: re.sub(r"\s", "", t)
        self.assertEqual(strip("".join(restored.groups)), "".join(groups))
        before = len(strip("".join(restored.groups[:restored.state.group_index])))
        self.assertLessEqual(before, 220)
        self.assertGreater(before + len(strip(restored.text)), 220)
        self.assertEqual(ReaderModel(self.store).state, restored.state)

    def test_regroup_state_save_failure_keeps_old_reference_and_document(self):
        import json
        from dataclasses import replace
        old_id = self.store.save_document("Book", ["字" * 350])
        path = self.store.directory / "documents" / (old_id + ".json")
        doc = json.loads(path.read_text(encoding="utf-8")); doc.pop("grouping_version")
        path.write_text(json.dumps(doc), encoding="utf-8")
        self.store.save_state(replace(self.model.state, document_id=old_id))
        before = (self.store.directory / "state.json").read_bytes()
        with patch.object(self.store, "save_state", side_effect=OSError("disk full")):
            with self.assertRaises(OSError):
                ReaderModel(self.store)
        self.assertEqual((self.store.directory / "state.json").read_bytes(), before)
        self.assertTrue(path.exists())
