"""test_dock_find.py

Tests for Dock entry finding and searching functionality.
"""

from tests.test_base import BaseDocklibTest


class TestDockFind(BaseDocklibTest):
    """Tests for Dock entry finding and searching methods."""

    def test_find_label(self):
        """Ensure docklib can find apps in the dock using findExistingLabel."""
        # NOTE: Only works if test environment is set to English language.
        app_idx = self.dock.findExistingLabel("Chess", section="persistent-apps")
        self.assertGreaterEqual(app_idx, 0)

        app_idx = self.dock.findExistingLabel("FooBarApp", section="persistent-apps")
        self.assertEqual(app_idx, -1)

    def test_find_entry_any(self):
        """Ensure docklib can find apps in the dock by any attribute."""
        app_idx = self.dock.findExistingEntry("Chess", section="persistent-apps")
        self.assertGreaterEqual(app_idx, 0)

        app_idx = self.dock.findExistingEntry("FooBarApp", section="persistent-apps")
        self.assertEqual(app_idx, -1)

    def test_find_entry_label(self):
        """Ensure docklib can find apps in the dock by label."""
        # NOTE: Only works if test environment is set to English language.
        app_idx = self.dock.findExistingEntry(
            "Chess", match_on="label", section="persistent-apps"
        )
        self.assertGreaterEqual(app_idx, 0)

        app_idx = self.dock.findExistingEntry(
            "FooBarApp", match_on="label", section="persistent-apps"
        )
        self.assertEqual(app_idx, -1)

    def test_find_entry_path(self):
        """Ensure docklib can find apps in the dock by path."""
        app_idx = self.dock.findExistingEntry(
            "/System/Applications/Chess.app", match_on="path", section="persistent-apps"
        )
        self.assertGreaterEqual(app_idx, 0)

        app_idx = self.dock.findExistingEntry(
            "/Applications/FooBarApp.app", match_on="path", section="persistent-apps"
        )
        self.assertEqual(app_idx, -1)

    def test_find_entry_ext(self):
        """Ensure docklib can find apps in the dock by filename with extension."""
        app_idx = self.dock.findExistingEntry(
            "Chess.app", match_on="name_ext", section="persistent-apps"
        )
        self.assertGreaterEqual(app_idx, 0)

        app_idx = self.dock.findExistingEntry(
            "FooBarApp.app", match_on="name_ext", section="persistent-apps"
        )
        self.assertEqual(app_idx, -1)

    def test_find_entry_noext(self):
        """Ensure docklib can find apps in the dock by filename without extension."""
        app_idx = self.dock.findExistingEntry(
            "Chess", match_on="name_noext", section="persistent-apps"
        )
        self.assertGreaterEqual(app_idx, 0)

        app_idx = self.dock.findExistingEntry(
            "FooBarApp", match_on="name_noext", section="persistent-apps"
        )
        self.assertEqual(app_idx, -1)

    def test_find_other(self):
        """Ensure docklib can find other items in the dock."""
        other_idx = self.dock.findExistingLabel(
            "Application Support", section="persistent-others"
        )
        self.assertGreaterEqual(other_idx, 0)

        other_idx = self.dock.findExistingLabel(
            "FooBarOther", section="persistent-others"
        )
        self.assertEqual(other_idx, -1)

    def test_find_url(self):
        """Ensure docklib can find url items in the dock."""
        # Add a URL item to our mock data for testing
        url_item = {
            "tile-type": "url-tile",
            "GUID": 12349,
            "tile-data": {"file-label": "Apple Inc", "url": "https://www.apple.com"},
        }
        self.dock.items["persistent-others"].append(url_item)

        other_idx = self.dock.findExistingLabel(
            "Apple Inc", section="persistent-others"
        )
        self.assertGreaterEqual(other_idx, 0)

    def test_find_existing_url(self):
        """Ensure docklib can find URL items by URL."""
        # Add a URL item to the dock
        url_item = {
            "tile-type": "url-tile",
            "tile-data": {
                "label": "GitHub",
                "url": {
                    "_CFURLString": "https://www.github.com/",
                    "_CFURLStringType": 15,
                },
            },
        }
        self.dock.items["persistent-others"].append(url_item)

        # Test finding existing URL
        found_index = self.dock.findExistingURL("https://www.github.com/")
        self.assertGreaterEqual(found_index, 0)

        # Test finding non-existing URL
        not_found_index = self.dock.findExistingURL("https://www.example.com/")
        self.assertEqual(not_found_index, -1)
