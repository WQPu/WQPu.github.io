"""Reject annotation mistakes and preserve publication versions during generation."""
import contextlib
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import generate_publications_data as publications


def source(**changes):
    value = {
        "schema_version": 1,
        "topic_definitions": [{"id": "sensing", "name": "Sensing", "description": "Detection and localization."}],
        "topics": {"example": ["sensing"]},
        "corresponding_authors": {"example": ["Wenqiang Pu", "Rui Zhou"]},
    }
    value.update(changes)
    return json.dumps(value)


class PublicationAnnotationsTest(unittest.TestCase):
    def test_topic_typo_cannot_silently_drop_a_paper(self):
        with self.assertRaisesRegex(ValueError, "Unknown.*topic"):
            publications.annotations(source(topics={"example": ["senisng"]}), {"example"})

    def test_stale_key_is_reported(self):
        with self.assertRaisesRegex(ValueError, "not found in bibliography"):
            publications.annotations(source(), {"renamed"})

    def test_duplicate_json_keys_cannot_silently_replace_annotations(self):
        document = source().replace('"topics": {', '"topics": {}, "topics": {')
        with self.assertRaisesRegex(ValueError, "Duplicate annotation key"):
            publications.annotations(document, {"example"})

    def test_missing_topic_source_is_reported(self):
        with self.assertRaisesRegex(ValueError, "Missing topic definitions"):
            publications.annotations(source(topic_definitions=[]), {"example"})

    def test_repeated_topic_memberships_are_rejected(self):
        with self.assertRaisesRegex(ValueError, "repeated topic"):
            publications.annotations(source(topics={"example": ["sensing", "sensing"]}), {"example"})

    def test_multiple_correspondents_are_preserved(self):
        _, _, names = publications.annotations(source(), {"example"})
        self.assertEqual(names["example"], ["Wenqiang Pu", "Rui Zhou"])

    def test_unknown_corresponding_status_remains_unknown(self):
        _, _, names = publications.annotations(source(corresponding_authors={}), {"example"})
        self.assertNotIn("example", names)

    def test_repeated_corresponding_names_are_rejected(self):
        with self.assertRaisesRegex(ValueError, "Duplicate corresponding-author"):
            publications.annotations(source(corresponding_authors={"example": ["Wenqiang Pu", "Wenqiang Pu"]}), {"example"})

    def test_unsupported_schema_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "Unsupported"):
            publications.annotations(source(schema_version=2), {"example"})

    def test_generator_does_not_need_the_local_pdf_folder(self):
        bib = """@article{example,
  title={Example},
  author={Pu, Wenqiang and Zhou, Rui},
  journal={IEEE Transactions on Signal Processing},
  year={2025},
}
@article{new,
  title={New research},
  author={Pu, Wenqiang},
  journal={SSRN preprint 1234567},
  year={2026},
}
"""
        with tempfile.TemporaryDirectory() as folder:
            folder = Path(folder)
            paths = {"BIB": folder / "papers.bib", "ANNOTATIONS": folder / "annotations.json", "OUT": folder / "years.json", "TOPICS_OUT": folder / "topics.json"}
            paths["BIB"].write_text(bib)
            paths["ANNOTATIONS"].write_text(source())
            with patch.multiple(publications, **paths), contextlib.redirect_stdout(io.StringIO()):
                publications.main()
            years = json.loads(paths["OUT"].read_text())
            topics = json.loads(paths["TOPICS_OUT"].read_text())
            new = years[0]["groups"][0]
            self.assertEqual(new["name"], "Preprints")
            self.assertEqual(new["items"][0]["corresponding_authors"], [])
            self.assertEqual(next(t for t in topics if t["id"] == "unclassified")["count"], 1)
            self.assertEqual(years[1]["groups"][0]["items"][0]["corresponding_authors"], ["Wenqiang Pu", "Rui Zhou"])

    def test_a_correspondent_must_appear_in_the_bibliography(self):
        with tempfile.TemporaryDirectory() as folder:
            folder = Path(folder)
            paths = {"BIB": folder / "papers.bib", "ANNOTATIONS": folder / "annotations.json", "OUT": folder / "years.json", "TOPICS_OUT": folder / "topics.json"}
            paths["BIB"].write_text("@article{example,\n title={Example},\n author={Pu, Wenqiang},\n journal={Journal},\n year={2025},\n}\n")
            paths["ANNOTATIONS"].write_text(source())
            with patch.multiple(publications, **paths), self.assertRaisesRegex(ValueError, "not in author list"):
                publications.main()


if __name__ == "__main__":
    unittest.main()
