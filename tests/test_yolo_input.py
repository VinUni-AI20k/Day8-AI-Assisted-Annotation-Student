"""Malformed label values must not enter training or submission checks."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from tools.yolo_io import read_yolo


class YoloInputTest(unittest.TestCase):
    def test_rejects_fractional_class_and_nonfinite_coordinates(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            label = Path(temp) / "label.txt"
            for bad in ("0.5 0.5 0.5 0.1 0.1\n", "0 NaN 0.5 0.1 0.1\n", "0 0.5 Inf 0.1 0.1\n"):
                with self.subTest(bad=bad):
                    label.write_text(bad, encoding="utf-8")
                    with self.assertRaises(ValueError):
                        read_yolo(label)


if __name__ == "__main__":
    unittest.main()
