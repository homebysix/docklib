"""Unit tests for docklib."""

import os
import types
import unittest
from time import sleep

import docklib


class TestDocklib(unittest.TestCase):
    """Unit test class."""

    def test_import(self):
        """Ensure docklib imports successfully as a module."""
        self.assertIs(type(docklib), types.ModuleType)

    def test_init(self):
        """Ensure docklib successfully reads the macOS dock."""
        dock = docklib.Dock()
        self.assertIsInstance(dock, docklib.Dock)

    def test_sections(self):
        """Ensure docklib retrieves the expected dock sections."""
        dock = docklib.Dock()
        actual_sections = list(dock.items.keys())
        # pylint: disable=W0212
        self.assertEqual(sorted(actual_sections), sorted(docklib.Dock._SECTIONS))
        # pylint: enable=W0212

    def test_item_keys(self):
        """Ensure docklib does not encounter unexpected dock item keys."""
        dock = docklib.Dock()
        sections = ["persistent-apps", "persistent-others"]
        actual_keys = []
        expected_keys = ["tile-type", "GUID", "tile-data"]
        for section in sections:
            for item in dock.items[section]:
                actual_keys.extend(list(item.keys()))
        actual_keys = list(set(actual_keys))
        self.assertEqual(sorted(actual_keys), sorted(expected_keys))

    def test_tile_data_keys(self):
        """Ensure docklib does not encounter unexpected tile-data keys."""
        dock = docklib.Dock()
        sections = ["persistent-apps", "persistent-others"]
        actual_keys = []
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
            "parent-mod-date",
            "preferreditemsize",
            "showas",
        ]
        for section in sections:
            for item in dock.items[section]:
                actual_keys.extend(list(item["tile-data"].keys()))
        actual_keys = list(set(actual_keys))
        self.assertEqual(sorted(actual_keys), sorted(expected_keys))

    def test_tile_types(self):
        """Ensure docklib does not encounter unexpected tile-types."""
        dock = docklib.Dock()
        sections = ["persistent-apps", "persistent-others"]
        actual_types = []
        expected_types = ["directory-tile", "file-tile"]
        for section in sections:
            actual_types.extend([x["tile-type"] for x in dock.items[section]])
        actual_types = list(set(actual_types))
        self.assertEqual(sorted(actual_types), sorted(expected_types))

    def test_add_app(self):
        """Ensure docklib can add apps to the dock."""
        dock = docklib.Dock()
        item = dock.makeDockAppEntry("/System/Applications/Chess.app")
        old_len = len(dock.items["persistent-apps"])
        dock.items["persistent-apps"].append(item)
        dock.save()
        sleep(2)
        new_len = len(dock.items["persistent-apps"])
        self.assertEqual(new_len, old_len + 1)

    def test_find_app(self):
        """Ensure docklib can find apps in the dock."""
        dock = docklib.Dock()
        app_idx = dock.findExistingLabel("Chess", section="persistent-apps")
        self.assertGreaterEqual(app_idx, 0)

        app_idx = dock.findExistingLabel("FooBarApp", section="persistent-apps")
        self.assertEqual(app_idx, -1)

    def test_remove_app(self):
        """Ensure docklib can remove apps from the dock."""
        dock = docklib.Dock()
        old_len = len(dock.items["persistent-apps"])
        dock.removeDockEntry("Chess")
        dock.save()
        sleep(2)
        new_len = len(dock.items["persistent-apps"])
        self.assertEqual(new_len, old_len - 1)

    def test_add_other(self):
        """Ensure docklib can add other items to the dock."""
        dock = docklib.Dock()
        item = dock.makeDockOtherEntry(
            os.path.expanduser("~/Library/Application Support")
        )
        old_len = len(dock.items["persistent-others"])
        dock.items["persistent-others"].append(item)
        dock.save()
        sleep(2)
        new_len = len(dock.items["persistent-others"])
        self.assertEqual(new_len, old_len + 1)

    def test_find_other(self):
        """Ensure docklib can find other items in the dock."""
        dock = docklib.Dock()
        other_idx = dock.findExistingLabel(
            "Application Support", section="persistent-others"
        )
        self.assertGreaterEqual(other_idx, 0)

        other_idx = dock.findExistingLabel("FooBarOther", section="persistent-others")
        self.assertEqual(other_idx, -1)

    def test_remove_other(self):
        """Ensure docklib can remove other items from the dock."""
        dock = docklib.Dock()
        old_len = len(dock.items["persistent-others"])
        dock.removeDockEntry("Application Support")
        dock.save()
        sleep(2)
        new_len = len(dock.items["persistent-others"])
        self.assertEqual(new_len, old_len - 1)


if __name__ == "__main__":
    unittest.main()
