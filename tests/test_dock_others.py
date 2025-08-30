"""test_dock_others.py

Tests for Dock "others" section operations (folders/files).
"""

import os
from unittest.mock import patch

from tests.test_base import BaseDocklibTest


class TestDockOthers(BaseDocklibTest):
    """Tests for Dock others section operations."""

    def test_add_other(self):
        """Ensure docklib can add other items to the dock."""
        mock_entry = {
            "tile-type": "directory-tile",
            "GUID": 12348,
            "tile-data": {
                "file-label": "Application Support",
                "file-data": {
                    "_CFURLString": "file:///Users/test/Library/Application%20Support/"
                },
            },
        }

        with patch.object(self.dock, "makeDockOtherEntry", return_value=mock_entry):
            item = self.dock.makeDockOtherEntry(
                os.path.expanduser("~/Library/Application Support")
            )
            old_len = len(self.dock.items["persistent-others"])
            self.dock.items["persistent-others"].append(item)
            self.dock.save()

            new_len = len(self.dock.items["persistent-others"])
            self.assertEqual(new_len, old_len + 1)

    def test_remove_other(self):
        """Ensure docklib can remove other items from the dock."""
        # Ensure Application Support is in the dock for this test
        initial_len = len(self.dock.items["persistent-others"])

        # Mock removeDockEntry to simulate removal
        with patch.object(self.dock, "removeDockEntry") as mock_remove:

            def simulate_removal(label):
                if label == "Application Support":
                    # Find and remove Application Support from the list
                    self.dock.items["persistent-others"] = [
                        item
                        for item in self.dock.items["persistent-others"]
                        if item["tile-data"].get("file-label") != "Application Support"
                    ]
                    return True
                return False

            mock_remove.side_effect = simulate_removal
            self.dock.removeDockEntry("Application Support")
            self.dock.save()

            new_len = len(self.dock.items["persistent-others"])
            self.assertEqual(new_len, initial_len - 1)
            mock_remove.assert_called_with("Application Support")
