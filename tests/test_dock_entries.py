"""test_dock_entries.py

Tests for general Dock entry operations (remove, replace by various criteria).
"""

from unittest.mock import patch

from tests.test_base import BaseDocklibTest


class TestDockEntries(BaseDocklibTest):
    """Tests for general Dock entry operations."""

    def test_remove_dock_entry_by_label(self):
        """Ensure docklib can remove dock entries by label."""
        # Add a test app to remove
        test_app = {
            "tile-type": "file-tile",
            "tile-data": {
                "file-data": {
                    "_CFURLString": "file:///Applications/Test%20App.app/",
                    "_CFURLStringType": 15,
                },
                "file-label": "Test App",
                "file-type": 41,
            },
        }
        self.dock.items["persistent-apps"].append(test_app)
        initial_count = len(self.dock.items["persistent-apps"])

        # Remove by label
        self.dock.removeDockEntry(
            "Test App", match_on="label", section="persistent-apps"
        )

        # Verify removal
        final_count = len(self.dock.items["persistent-apps"])
        self.assertEqual(final_count, initial_count - 1)

        # Verify the app is no longer found
        found_index = self.dock.findExistingEntry(
            "Test App", match_on="label", section="persistent-apps"
        )
        self.assertEqual(found_index, -1)

    def test_remove_dock_entry_by_path(self):
        """Ensure docklib can remove dock entries by path."""
        # Add a test app to remove
        test_path = "/Applications/Test App.app"
        test_app = {
            "tile-type": "file-tile",
            "tile-data": {
                "file-data": {
                    "_CFURLString": "file:///Applications/Test%20App.app/",
                    "_CFURLStringType": 15,
                },
                "file-label": "Test App",
                "file-type": 41,
            },
        }
        self.dock.items["persistent-apps"].append(test_app)
        initial_count = len(self.dock.items["persistent-apps"])

        # Remove by path
        self.dock.removeDockEntry(test_path, match_on="path", section="persistent-apps")

        # Verify removal
        final_count = len(self.dock.items["persistent-apps"])
        self.assertEqual(final_count, initial_count - 1)

    def test_remove_dock_entry_all_sections(self):
        """Ensure docklib can remove dock entries from all sections when no section specified."""
        # Add test items to both sections
        test_app = {
            "tile-type": "file-tile",
            "tile-data": {
                "file-data": {
                    "_CFURLString": "file:///Applications/Test%20App.app/",
                    "_CFURLStringType": 15,
                },
                "file-label": "Test App",
                "file-type": 41,
            },
        }
        test_folder = {
            "tile-type": "directory-tile",
            "tile-data": {
                "file-data": {
                    "_CFURLString": "file:///Users/test/Test%20Folder/",
                    "_CFURLStringType": 15,
                },
                "file-label": "Test Folder",
                "arrangement": 1,
                "displayas": 1,
                "showas": 0,
                "dock-extra": False,
            },
        }

        self.dock.items["persistent-apps"].append(test_app)
        self.dock.items["persistent-others"].append(test_folder)

        initial_apps_count = len(self.dock.items["persistent-apps"])
        initial_others_count = len(self.dock.items["persistent-others"])

        # Remove from all sections (should find and remove the app)
        self.dock.removeDockEntry("Test App", match_on="label")

        # Verify removal from apps section
        final_apps_count = len(self.dock.items["persistent-apps"])
        self.assertEqual(final_apps_count, initial_apps_count - 1)

        # Verify others section unchanged
        final_others_count = len(self.dock.items["persistent-others"])
        self.assertEqual(final_others_count, initial_others_count)

    def test_remove_dock_entry_nonexistent(self):
        """Ensure removing non-existent dock entry doesn't cause errors."""
        initial_apps_count = len(self.dock.items["persistent-apps"])
        initial_others_count = len(self.dock.items["persistent-others"])

        # Try to remove non-existent item
        self.dock.removeDockEntry("Nonexistent App", match_on="label")

        # Verify no changes
        final_apps_count = len(self.dock.items["persistent-apps"])
        final_others_count = len(self.dock.items["persistent-others"])
        self.assertEqual(final_apps_count, initial_apps_count)
        self.assertEqual(final_others_count, initial_others_count)

    def test_replace_dock_entry_by_match_str(self):
        """Ensure docklib can replace dock entries using match_str."""
        # Add a test app to replace
        old_app = {
            "tile-type": "file-tile",
            "tile-data": {
                "file-data": {
                    "_CFURLString": "file:///Applications/Old%20App.app/",
                    "_CFURLStringType": 15,
                },
                "file-label": "Old App",
                "file-type": 41,
            },
        }
        self.dock.items["persistent-apps"].append(old_app)

        # Mock the makeDockAppEntry to return a predictable result
        with patch.object(self.dock, "makeDockAppEntry") as mock_make_entry:
            new_app = {
                "tile-type": "file-tile",
                "tile-data": {
                    "file-data": {
                        "_CFURLString": "file:///Applications/New%20App.app/",
                        "_CFURLStringType": 15,
                    },
                    "file-label": "New App",
                    "file-type": 41,
                },
            }
            mock_make_entry.return_value = new_app

            # Replace the app
            self.dock.replaceDockEntry(
                "/Applications/New App.app", match_str="Old App", match_on="label"
            )

            # Verify the replacement
            found_index = self.dock.findExistingEntry("New App", match_on="label")
            self.assertGreaterEqual(found_index, 0)

            # Verify old app is gone
            old_index = self.dock.findExistingEntry("Old App", match_on="label")
            self.assertEqual(old_index, -1)

    def test_replace_dock_entry_auto_match(self):
        """Ensure docklib can replace dock entries using auto-derived match string."""
        # Add a test app to replace
        old_app = {
            "tile-type": "file-tile",
            "tile-data": {
                "file-data": {
                    "_CFURLString": "file:///Applications/TestApp.app/",
                    "_CFURLStringType": 15,
                },
                "file-label": "TestApp",
                "file-type": 41,
            },
        }
        self.dock.items["persistent-apps"].append(old_app)

        # Mock the makeDockAppEntry to return a predictable result
        with patch.object(self.dock, "makeDockAppEntry") as mock_make_entry:
            new_app = {
                "tile-type": "file-tile",
                "tile-data": {
                    "file-data": {
                        "_CFURLString": "file:///Applications/NewTestApp.app/",
                        "_CFURLStringType": 15,
                    },
                    "file-label": "NewTestApp",
                    "file-type": 41,
                },
            }
            mock_make_entry.return_value = new_app

            # Replace using filename without extension (should auto-derive match_str)
            self.dock.replaceDockEntry("/Applications/TestApp.app")

            # Verify the replacement occurred
            found_index = self.dock.findExistingEntry("NewTestApp", match_on="label")
            self.assertGreaterEqual(found_index, 0)

    def test_replace_dock_entry_nonexistent(self):
        """Ensure replacing non-existent dock entry doesn't cause errors."""
        initial_count = len(self.dock.items["persistent-apps"])

        # Mock the makeDockAppEntry
        with patch.object(self.dock, "makeDockAppEntry") as mock_make_entry:
            new_app = {
                "tile-type": "file-tile",
                "tile-data": {
                    "file-data": {
                        "_CFURLString": "file:///Applications/New%20App.app/",
                        "_CFURLStringType": 15,
                    },
                    "file-label": "New App",
                    "file-type": 41,
                },
            }
            mock_make_entry.return_value = new_app

            # Try to replace non-existent item
            self.dock.replaceDockEntry(
                "/Applications/New App.app", match_str="Nonexistent App"
            )

            # Verify no changes
            final_count = len(self.dock.items["persistent-apps"])
            self.assertEqual(final_count, initial_count)

    def test_replace_dock_entry_other_section(self):
        """Ensure docklib can replace entries in persistent-others section."""
        # Add a test folder to replace
        old_folder = {
            "tile-type": "directory-tile",
            "tile-data": {
                "file-data": {
                    "_CFURLString": "file:///Users/test/Old%20Folder/",
                    "_CFURLStringType": 15,
                },
                "file-label": "Old Folder",
                "arrangement": 1,
                "displayas": 1,
                "showas": 0,
                "dock-extra": False,
            },
        }
        self.dock.items["persistent-others"].append(old_folder)

        # Mock the makeDockOtherEntry
        with patch.object(self.dock, "makeDockOtherEntry") as mock_make_entry:
            new_folder = {
                "tile-type": "directory-tile",
                "tile-data": {
                    "file-data": {
                        "_CFURLString": "file:///Users/test/New%20Folder/",
                        "_CFURLStringType": 15,
                    },
                    "file-label": "New Folder",
                    "arrangement": 1,
                    "displayas": 1,
                    "showas": 0,
                    "dock-extra": False,
                },
            }
            mock_make_entry.return_value = new_folder

            # Replace the folder
            self.dock.replaceDockEntry(
                "/Users/test/New Folder",
                match_str="Old Folder",
                match_on="label",
                section="persistent-others",
            )

            # Verify the replacement
            found_index = self.dock.findExistingEntry(
                "New Folder", match_on="label", section="persistent-others"
            )
            self.assertGreaterEqual(found_index, 0)
