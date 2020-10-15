"""Unit tests for docklib."""

import os
import types
import unittest
from time import sleep

import docklib


class TestDocklib(unittest.TestCase):
    """Unit test class."""

    def setUp(self):
        self.dock = docklib.Dock()

    def test_import(self):
        """Ensure docklib imports successfully as a module."""
        self.assertIs(type(docklib), types.ModuleType)

    def test_init(self):
        """Ensure docklib successfully reads the macOS dock."""
        self.assertIsInstance(self.dock, docklib.Dock)

    def test_sections(self):
        """Ensure docklib retrieves the expected dock sections."""
        actual_sections = list(self.dock.items.keys())
        # pylint: disable=W0212
        self.assertEqual(sorted(actual_sections), sorted(docklib.Dock._SECTIONS))
        # pylint: enable=W0212

    def test_item_keys(self):
        """Ensure docklib does not encounter unexpected dock item keys."""
        sections = ["persistent-apps", "persistent-others"]
        actual_keys = []
        expected_keys = ["tile-type", "GUID", "tile-data"]
        for section in sections:
            for item in self.dock.items[section]:
                actual_keys.extend(list(item.keys()))
        actual_keys = list(set(actual_keys))
        self.assertEqual(sorted(actual_keys), sorted(expected_keys))

    def test_tile_data_keys(self):
        """Ensure docklib does not encounter unexpected tile-data keys."""
        sections = ["persistent-apps", "persistent-others"]
        expected_keys = [
            "arrangement",
            "book",
            "bundle-identifier",
            "displayas",
            "dock-extra",
            "file-data",
            "file-label",
            "file-mod-date",
            "file-type",
            "label",
            "parent-mod-date",
            "preferreditemsize",
            "showas",
            "url",
        ]
        for section in sections:
            for item in self.dock.items[section]:
                for key in item["tile-data"].keys():
                    self.assertIn(key, expected_keys)

    def test_tile_types(self):
        """Ensure docklib does not encounter unexpected tile-types."""
        sections = ["persistent-apps", "persistent-others"]
        expected_types = [
            "directory-tile",
            "file-tile",
            "small-spacer-tile",
            "spacer-tile",
            "url-tile",
        ]
        for section in sections:
            for item in self.dock.items[section]:
                self.assertIn(item["tile-type"], expected_types)

    def test_add_app(self):
        """Ensure docklib can add apps to the dock."""
        item = self.dock.makeDockAppEntry("/System/Applications/Chess.app")
        old_len = len(self.dock.items["persistent-apps"])
        self.dock.items["persistent-apps"].append(item)
        self.dock.save()
        sleep(2)
        new_len = len(self.dock.items["persistent-apps"])
        self.assertEqual(new_len, old_len + 1)

    def test_find_app(self):
        """Ensure docklib can find apps in the dock."""
        app_idx = self.dock.findExistingLabel("Chess", section="persistent-apps")
        self.assertGreaterEqual(app_idx, 0)

        app_idx = self.dock.findExistingLabel("FooBarApp", section="persistent-apps")
        self.assertEqual(app_idx, -1)

    def test_remove_app(self):
        """Ensure docklib can remove apps from the dock."""
        old_len = len(self.dock.items["persistent-apps"])
        self.dock.removeDockEntry("Chess")
        self.dock.save()
        sleep(2)
        new_len = len(self.dock.items["persistent-apps"])
        self.assertEqual(new_len, old_len - 1)

    def test_add_other(self):
        """Ensure docklib can add other items to the dock."""
        item = self.dock.makeDockOtherEntry(
            os.path.expanduser("~/Library/Application Support")
        )
        old_len = len(self.dock.items["persistent-others"])
        self.dock.items["persistent-others"].append(item)
        self.dock.save()
        sleep(2)
        new_len = len(self.dock.items["persistent-others"])
        self.assertEqual(new_len, old_len + 1)

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

    def test_remove_other(self):
        """Ensure docklib can remove other items from the dock."""
        old_len = len(self.dock.items["persistent-others"])
        self.dock.removeDockEntry("Application Support")
        self.dock.save()
        sleep(2)
        new_len = len(self.dock.items["persistent-others"])
        self.assertEqual(new_len, old_len - 1)

    def test_add_url(self):
        """Ensure docklib can add url items to the dock."""
        item = self.dock.makeDockOtherURLEntry("https://www.apple.com", "Apple Inc")
        old_len = len(self.dock.items["persistent-others"])
        self.dock.items["persistent-others"].append(item)
        self.dock.save()
        sleep(2)
        new_len = len(self.dock.items["persistent-others"])
        self.assertEqual(new_len, old_len + 1)

    def test_remove_url(self):
        """Ensure docklib can remove url items from the dock."""
        old_len = len(self.dock.items["persistent-others"])
        self.dock.removeDockURLEntry("https://www.apple.com")
        self.dock.save()
        sleep(2)
        new_len = len(self.dock.items["persistent-others"])
        self.assertEqual(new_len, old_len - 1)

    def test_add_spacer(self):
        """Ensure docklib can add a spacer item to the dock."""
        item = self.dock.makeDockAppSpacer()
        old_len = len(self.dock.items["persistent-apps"])
        self.dock.items["persistent-apps"].insert(0, item)
        self.dock.save()
        sleep(2)
        new_len = len(self.dock.items["persistent-apps"])
        self.assertEqual(new_len, old_len + 1)

    def test_remove_spacer(self):
        """Ensure docklib can remove a spacer item from the dock."""
        old_len = len(self.dock.items["persistent-apps"])
        del self.dock.items["persistent-apps"][0]
        self.dock.save()
        sleep(2)
        new_len = len(self.dock.items["persistent-apps"])
        self.assertEqual(new_len, old_len - 1)


if __name__ == "__main__":
    unittest.main()
