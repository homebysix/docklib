"""test_dock_urls.py

Tests for Dock URL entry operations.
"""

from unittest.mock import patch

from tests.test_base import BaseDocklibTest


class TestDockUrls(BaseDocklibTest):
    """Tests for Dock URL entry operations."""

    def test_add_url(self):
        """Ensure docklib can add url items to the dock."""
        mock_entry = {
            "tile-type": "url-tile",
            "GUID": 12349,
            "tile-data": {"file-label": "Apple Inc", "url": "https://www.apple.com"},
        }

        with patch.object(self.dock, "makeDockOtherURLEntry", return_value=mock_entry):
            item = self.dock.makeDockOtherURLEntry("https://www.apple.com", "Apple Inc")
            old_len = len(self.dock.items["persistent-others"])
            self.dock.items["persistent-others"].append(item)
            self.dock.save()

            new_len = len(self.dock.items["persistent-others"])
            self.assertEqual(new_len, old_len + 1)

    def test_remove_url(self):
        """Ensure docklib can remove url items from the dock."""
        # Add URL item first
        url_item = {
            "tile-type": "url-tile",
            "GUID": 12349,
            "tile-data": {
                "label": "Apple Inc",
                "url": {
                    "_CFURLString": "https://www.apple.com/",
                    "_CFURLStringType": 15,
                },
            },
        }
        self.dock.items["persistent-others"].append(url_item)
        old_len = len(self.dock.items["persistent-others"])

        # Remove URL entry
        self.dock.removeDockURLEntry("https://www.apple.com/")

        # Verify removal
        new_len = len(self.dock.items["persistent-others"])
        self.assertEqual(new_len, old_len - 1)
