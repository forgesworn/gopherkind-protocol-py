from __future__ import annotations

import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from gopherkind_protocol import (  # noqa: E402
    current_document,
    parse_document,
    parse_kindmap,
    render_type0,
    replacement_winner,
    url_path,
    valid_path,
)

FIXTURE = json.loads((ROOT / "tests/fixtures/kind31436-v2.json").read_text())


class PublishedFixtureTest(unittest.TestCase):
    def test_document_metadata(self) -> None:
        self.assertEqual(FIXTURE["version"], 2)
        for vector in FIXTURE["documents"]:
            with self.subTest(vector["name"]):
                parsed = parse_document(vector["event"])
                self.assertEqual(parsed is not None, vector["valid"])
                if parsed is not None:
                    self.assertEqual(
                        {"path": parsed.path, "type": parsed.type, "title": parsed.title},
                        vector["meta"],
                    )

    def test_exact_paths_and_url_encoding(self) -> None:
        for vector in FIXTURE["paths"]:
            with self.subTest(vector["value"]):
                self.assertEqual(valid_path(vector["value"]), vector["valid"])
                if "urlPath" in vector:
                    self.assertEqual(url_path(vector["value"]), vector["urlPath"])
        for left, right in FIXTURE["distinctPaths"]:
            self.assertNotEqual(left, right)

    def test_kindmap(self) -> None:
        for vector in FIXTURE["kindmap"]:
            with self.subTest(vector["name"]):
                actual = [line.as_fixture_value() for line in parse_kindmap(vector["input"])]
                self.assertEqual(actual, vector["output"])

    def test_replacement_then_validation_and_expiry(self) -> None:
        for vector in FIXTURE["replacement"]:
            events = [
                {"kind": 31436, "content": "", **event}
                for event in vector["events"]
            ]
            with self.subTest(vector["name"]):
                winner = replacement_winner(events)
                visible = current_document(events, vector["now"])
                self.assertEqual(winner["id"] if winner else None, vector["winner"])
                self.assertEqual(visible["id"] if visible else None, vector["visible"])

    def test_type0_wire(self) -> None:
        for vector in FIXTURE["type0Wire"]:
            with self.subTest(repr(vector["input"])):
                self.assertEqual(render_type0(vector["input"]), vector["output"])


if __name__ == "__main__":
    unittest.main()
