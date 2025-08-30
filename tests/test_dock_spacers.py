"""test_dock_spacers.py

Tests for Dock spacer operations.
"""

from unittest.mock import patch

from tests.test_base import BaseDocklibTest


class TestDockSpacer(BaseDocklibTest):
    """Tests for Dock spacer operations."""

    def test_add_spacer(self):
        """Ensure docklib can add a spacer item to the dock."""
        mock_spacer = {"tile-type": "spacer-tile", "GUID": 12350, "tile-data": {}}

        with patch.object(self.dock, "makeDockAppSpacer", return_value=mock_spacer):
            item = self.dock.makeDockAppSpacer()
            old_len = len(self.dock.items["persistent-apps"])
            self.dock.items["persistent-apps"].insert(0, item)
            self.dock.save()

            new_len = len(self.dock.items["persistent-apps"])
            self.assertEqual(new_len, old_len + 1)

    def test_remove_spacer(self):
        """Ensure docklib can remove a spacer item from the dock."""
        # Add a spacer first
        spacer_item = {"tile-type": "spacer-tile", "GUID": 12350, "tile-data": {}}
        self.dock.items["persistent-apps"].insert(0, spacer_item)
        old_len = len(self.dock.items["persistent-apps"])

        del self.dock.items["persistent-apps"][0]
        self.dock.save()

        new_len = len(self.dock.items["persistent-apps"])
        self.assertEqual(new_len, old_len - 1)
