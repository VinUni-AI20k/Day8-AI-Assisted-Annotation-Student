"""The independent scan must stay identical after it is locked."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from tools import lock_blind


class BlindLockTest(unittest.TestCase):
    def test_lock_detects_later_changes(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            reports = Path(temp)
            scan = reports / "BLIND_SCAN.md"
            lock = reports / "blind_lock.json"
            scan.write_text("Frame: frame_0000.jpg\nSố xe: 12\n", encoding="utf-8")
            with patch.object(lock_blind, "SCAN", scan), patch.object(lock_blind, "LOCK", lock):
                self.assertEqual(lock_blind.main(), 0)
                self.assertTrue(lock_blind.valid_lock())
                scan.write_text("Frame: frame_0000.jpg\nSố xe: 13\n", encoding="utf-8")
                self.assertFalse(lock_blind.valid_lock())
                self.assertEqual(lock_blind.main(), 1)


if __name__ == "__main__":
    unittest.main()
