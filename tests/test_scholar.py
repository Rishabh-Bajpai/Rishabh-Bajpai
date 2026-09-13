import importlib.util
import json
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import patch


SCRIPT = Path(__file__).parents[1] / "scripts" / "scholar.py"
SPEC = importlib.util.spec_from_file_location("scholar", SCRIPT)
scholar = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(scholar)


class ScholarTests(unittest.TestCase):
    def test_parse_metrics(self):
        html = (
            '<meta content="Cited by 700" />'
            '<td>h-index</a></td><td class="gsc_rsb_std">11</td>'
            '<td>i10-index</a></td><td class="gsc_rsb_std">12</td>'
        )

        self.assertEqual(
            scholar.parse_metrics(html),
            {"citations": 700, "h_index": 11, "i10": 12},
        )

    def test_failed_fetch_preserves_values_and_updates_date(self):
        with tempfile.TemporaryDirectory() as directory:
            output_dir = Path(directory)
            for filename, value in (
                ("gs_data_citations.json", "646"),
                ("gs_data_h_index.json", "9"),
                ("gs_data_i10_index.json", "9"),
            ):
                (output_dir / filename).write_text(json.dumps({"message": value}))

            with patch.object(scholar, "fetch", return_value=""):
                result = scholar.update(output_dir)

            self.assertEqual(result["citations"], 646)
            self.assertEqual(result["h_index"], 9)
            self.assertEqual(result["i10"], 9)
            self.assertEqual(
                result["last_updated"], datetime.now(timezone.utc).date().isoformat()
            )
            self.assertEqual(
                json.loads((output_dir / "gs_data_last_updated.json").read_text())["message"],
                result["last_updated"],
            )
            self.assertEqual(
                set(result["used_fallback"]), {"citations", "h_index", "i10"}
            )

    def test_successful_fetch_replaces_values(self):
        html = (
            '<meta content="Cited by 700" />'
            '<td>h-index</a></td><td class="gsc_rsb_std">11</td>'
            '<td>i10-index</a></td><td class="gsc_rsb_std">12</td>'
        )

        with tempfile.TemporaryDirectory() as directory:
            with patch.object(scholar, "fetch", return_value=html):
                result = scholar.update(directory)

            self.assertEqual(result["citations"], 700)
            self.assertEqual(result["h_index"], 11)
            self.assertEqual(result["i10"], 12)
            self.assertEqual(result["used_fallback"], [])


if __name__ == "__main__":
    unittest.main()
