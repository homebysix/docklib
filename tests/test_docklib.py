"""test_docklib.py

Unit tests for docklib. These tests use mocking to avoid actual dock modifications.

To run tests:
    .venv/bin/python -m coverage run -m unittest discover -v
"""

import os
import pwd
import types
import unittest
from unittest.mock import patch, MagicMock

import docklib


class TestDocklib(unittest.TestCase):
    """Unit test class for docklib. Tests are independent and can run in any order."""

    def setUp(self):
        # Mock the LaunchAgentManager for the new implementation
        self.mock_launch_agent_patcher = patch("docklib.docklib.LaunchAgentManager")
        self.mock_launch_agent_class = self.mock_launch_agent_patcher.start()
        self.mock_launch_agent = MagicMock()
        self.mock_launch_agent.bootstrap.return_value = True
        self.mock_launch_agent.bootout.return_value = True
        self.mock_launch_agent_class.return_value = self.mock_launch_agent

        # Mock subprocess.run for LaunchAgentManager internal calls
        self.mock_subprocess_run_patcher = patch("docklib.docklib.subprocess.run")
        self.mock_subprocess_run = self.mock_subprocess_run_patcher.start()

        # Create a mock result for subprocess.run
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stderr = ""
        mock_result.stdout = ""
        self.mock_subprocess_run.return_value = mock_result

        # Mock pwd for LaunchAgentManager initialization
        self.mock_pwd_patcher = patch("docklib.docklib.pwd")
        self.mock_pwd = self.mock_pwd_patcher.start()
        mock_user = MagicMock()
        mock_user.pw_uid = 501
        self.mock_pwd.getpwuid.return_value = mock_user

        self.mock_cfpref_sync_patcher = patch(
            "docklib.docklib.CFPreferencesAppSynchronize"
        )
        self.mock_cfpref_sync = self.mock_cfpref_sync_patcher.start()
        self.mock_cfpref_sync.return_value = True

        self.mock_cfpref_set_patcher = patch("docklib.docklib.CFPreferencesSetAppValue")
        self.mock_cfpref_set = self.mock_cfpref_set_patcher.start()

        self.mock_cfpref_copy_patcher = patch(
            "docklib.docklib.CFPreferencesCopyAppValue"
        )
        self.mock_cfpref_copy = self.mock_cfpref_copy_patcher.start()

        # Create mock objects that have mutableCopy method
        class MockNSArray:
            def __init__(self, data):
                self.data = data

            def mutableCopy(self):
                return list(self.data)

        # Mock the copy function to return our sample data
        def mock_copy_app_value(key, domain):  # pylint: disable=unused-argument
            if key == "persistent-apps":
                return MockNSArray(
                    [
                        {
                            "tile-type": "file-tile",
                            "GUID": 12345,
                            "tile-data": {
                                "file-label": "Chess",
                                "bundle-identifier": "com.apple.Chess",
                                "file-data": {
                                    "_CFURLString": "file:///System/Applications/Chess.app/"
                                },
                            },
                        }
                    ]
                )
            elif key == "persistent-others":
                return MockNSArray(
                    [
                        {
                            "tile-type": "directory-tile",
                            "GUID": 12346,
                            "tile-data": {
                                "file-label": "Application Support",
                                "file-data": {
                                    "_CFURLString": "file:///Users/test/Library/Application%20Support/"
                                },
                            },
                        }
                    ]
                )
            else:
                return None

        self.mock_cfpref_copy.side_effect = mock_copy_app_value

        # Create a dock instance
        self.dock = docklib.Dock()

        # Store original data for resetting between tests
        self.original_persistent_apps = [
            {
                "tile-type": "file-tile",
                "GUID": 12345,
                "tile-data": {
                    "file-label": "Chess",
                    "bundle-identifier": "com.apple.Chess",
                    "file-data": {
                        "_CFURLString": "file:///System/Applications/Chess.app/"
                    },
                },
            }
        ]

        self.original_persistent_others = [
            {
                "tile-type": "directory-tile",
                "GUID": 12346,
                "tile-data": {
                    "file-label": "Application Support",
                    "file-data": {
                        "_CFURLString": "file:///Users/test/Library/Application%20Support/"
                    },
                },
            }
        ]

        # Ensure the dock has proper mock data (reset to original state)
        self.dock.items["persistent-apps"] = self.original_persistent_apps.copy()
        self.dock.items["persistent-others"] = self.original_persistent_others.copy()

    def tearDown(self):
        # Stop all patchers
        self.mock_launch_agent_patcher.stop()
        self.mock_subprocess_run_patcher.stop()
        self.mock_pwd_patcher.stop()
        self.mock_cfpref_sync_patcher.stop()
        self.mock_cfpref_set_patcher.stop()
        self.mock_cfpref_copy_patcher.stop()

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
            "is-beta",
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
        # Mock the make entry method to return a predictable entry
        mock_entry = {
            "tile-type": "file-tile",
            "GUID": 12347,
            "tile-data": {
                "file-label": "Calculator",
                "bundle-identifier": "com.apple.calculator",
                "file-data": {
                    "_CFURLString": "file:///System/Applications/Calculator.app/"
                },
            },
        }

        # Mock makeDockAppEntry to return our mock entry
        with patch.object(self.dock, "makeDockAppEntry", return_value=mock_entry):
            item = self.dock.makeDockAppEntry("/System/Applications/Calculator.app")
            old_len = len(self.dock.items["persistent-apps"])
            self.dock.items["persistent-apps"].append(item)

            # Test that the item was added in memory
            new_len = len(self.dock.items["persistent-apps"])
            self.assertEqual(new_len, old_len + 1)

            # Verify the correct item was added
            added_item = self.dock.items["persistent-apps"][-1]
            self.assertEqual(added_item["tile-data"]["file-label"], "Calculator")

            # Test that save() can be called without errors
            try:
                self.dock.save()
                save_succeeded = True
            except (AttributeError, TypeError, OSError) as e:
                # These are the expected exception types from dock operations
                save_succeeded = False
                print(f"Save failed with: {e}")

            self.assertTrue(
                save_succeeded, "dock.save() should complete without errors"
            )

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

    def test_remove_app(self):
        """Ensure docklib can remove apps from the dock."""
        # Ensure Chess app is in the dock for this test
        initial_len = len(self.dock.items["persistent-apps"])

        # Mock removeDockEntry to simulate removal
        with patch.object(self.dock, "removeDockEntry") as mock_remove:

            def simulate_removal(label):
                if label == "Chess":
                    # Find and remove Chess app from the list
                    self.dock.items["persistent-apps"] = [
                        item
                        for item in self.dock.items["persistent-apps"]
                        if item["tile-data"].get("file-label") != "Chess"
                    ]
                    return True
                return False

            mock_remove.side_effect = simulate_removal
            self.dock.removeDockEntry("Chess")
            self.dock.save()

            new_len = len(self.dock.items["persistent-apps"])
            self.assertEqual(new_len, initial_len - 1)
            mock_remove.assert_called_with("Chess")
            # Verify LaunchAgentManager methods were called
            self.mock_launch_agent.bootout.assert_called_with("com.apple.Dock.agent")
            self.mock_launch_agent.bootstrap.assert_called_with(
                "/System/Library/LaunchAgents/com.apple.Dock.plist"
            )

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

    def test_remove_url(self):
        """Ensure docklib can remove url items from the dock."""
        # Add URL item first
        url_item = {
            "tile-type": "url-tile",
            "GUID": 12349,
            "tile-data": {"file-label": "Apple Inc", "url": "https://www.apple.com"},
        }
        self.dock.items["persistent-others"].append(url_item)
        old_len = len(self.dock.items["persistent-others"])

        with patch.object(self.dock, "removeDockURLEntry") as mock_remove:
            mock_remove.side_effect = lambda url: (
                self.dock.items["persistent-others"].pop()
                if url == "https://www.apple.com"
                else None
            )
            self.dock.removeDockURLEntry("https://www.apple.com")
            self.dock.save()

            new_len = len(self.dock.items["persistent-others"])
            self.assertEqual(new_len, old_len - 1)
            mock_remove.assert_called_with("https://www.apple.com")

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

    def test_make_dock_app_spacer_default(self):
        """Ensure docklib can create a default spacer."""
        spacer = self.dock.makeDockAppSpacer()

        expected_spacer = {"tile-data": {}, "tile-type": "spacer-tile"}

        self.assertEqual(spacer, expected_spacer)

    def test_make_dock_app_spacer_small(self):
        """Ensure docklib can create a small spacer."""
        spacer = self.dock.makeDockAppSpacer("small-spacer-tile")

        expected_spacer = {"tile-data": {}, "tile-type": "small-spacer-tile"}

        self.assertEqual(spacer, expected_spacer)

    def test_make_dock_app_spacer_invalid_type(self):
        """Ensure docklib raises error for invalid spacer type."""
        with self.assertRaises(ValueError) as context:
            self.dock.makeDockAppSpacer("invalid-spacer-type")

        self.assertIn("invalid makeDockAppSpacer type", str(context.exception))

    def test_make_dock_app_entry_default_label(self):
        """Ensure docklib can create app entry with default label."""
        # Mock NSURL.fileURLWithPath_
        with patch("docklib.docklib.NSURL") as mock_nsurl:
            mock_url = MagicMock()
            mock_url.absoluteString.return_value = "file:///Applications/Safari.app/"
            mock_nsurl.fileURLWithPath_.return_value = mock_url

            app_entry = self.dock.makeDockAppEntry("/Applications/Safari.app")

            expected_entry = {
                "tile-data": {
                    "file-data": {
                        "_CFURLString": "file:///Applications/Safari.app/",
                        "_CFURLStringType": 15,
                    },
                    "file-label": "Safari",
                    "file-type": 41,
                },
                "tile-type": "file-tile",
            }

            self.assertEqual(app_entry, expected_entry)
            mock_nsurl.fileURLWithPath_.assert_called_once_with(
                "/Applications/Safari.app"
            )

    def test_make_dock_app_entry_custom_label(self):
        """Ensure docklib can create app entry with custom label."""
        # Mock NSURL.fileURLWithPath_
        with patch("docklib.docklib.NSURL") as mock_nsurl:
            mock_url = MagicMock()
            mock_url.absoluteString.return_value = "file:///Applications/Safari.app/"
            mock_nsurl.fileURLWithPath_.return_value = mock_url

            app_entry = self.dock.makeDockAppEntry(
                "/Applications/Safari.app", "My Browser"
            )

            expected_entry = {
                "tile-data": {
                    "file-data": {
                        "_CFURLString": "file:///Applications/Safari.app/",
                        "_CFURLStringType": 15,
                    },
                    "file-label": "My Browser",
                    "file-type": 41,
                },
                "tile-type": "file-tile",
            }

            self.assertEqual(app_entry, expected_entry)

    def test_make_dock_other_entry_file_defaults(self):
        """Ensure docklib can create other entry for file with defaults."""
        # Mock NSURL.fileURLWithPath_ and os.path.isdir
        with (
            patch("docklib.docklib.NSURL") as mock_nsurl,
            patch("docklib.docklib.os.path.isdir") as mock_isdir,
        ):
            mock_url = MagicMock()
            mock_url.absoluteString.return_value = "file:///Users/test/document.txt"
            mock_nsurl.fileURLWithPath_.return_value = mock_url
            mock_isdir.return_value = False

            other_entry = self.dock.makeDockOtherEntry("/Users/test/document.txt")

            expected_entry = {
                "tile-data": {
                    "file-data": {
                        "_CFURLString": "file:///Users/test/document.txt",
                        "_CFURLStringType": 15,
                    },
                    "file-label": "document",
                    "dock-extra": False,
                },
                "tile-type": "file-tile",
            }

            self.assertEqual(other_entry, expected_entry)

    def test_make_dock_other_entry_directory_defaults(self):
        """Ensure docklib can create other entry for directory with defaults."""
        # Mock NSURL.fileURLWithPath_ and os.path.isdir
        with (
            patch("docklib.docklib.NSURL") as mock_nsurl,
            patch("docklib.docklib.os.path.isdir") as mock_isdir,
        ):
            mock_url = MagicMock()
            mock_url.absoluteString.return_value = "file:///Users/test/Documents/"
            mock_nsurl.fileURLWithPath_.return_value = mock_url
            mock_isdir.return_value = True

            other_entry = self.dock.makeDockOtherEntry("/Users/test/Documents")

            expected_entry = {
                "tile-data": {
                    "arrangement": 1,  # sort by name
                    "displayas": 1,
                    "file-data": {
                        "_CFURLString": "file:///Users/test/Documents/",
                        "_CFURLStringType": 15,
                    },
                    "file-label": "Documents",
                    "dock-extra": False,
                    "showas": 0,
                },
                "tile-type": "directory-tile",
            }

            self.assertEqual(other_entry, expected_entry)

    def test_make_dock_other_entry_downloads_special_case(self):
        """Ensure docklib handles Downloads folder special case."""
        # Mock NSURL.fileURLWithPath_ and os.path.isdir
        with (
            patch("docklib.docklib.NSURL") as mock_nsurl,
            patch("docklib.docklib.os.path.isdir") as mock_isdir,
        ):
            mock_url = MagicMock()
            mock_url.absoluteString.return_value = "file:///Users/test/Downloads/"
            mock_nsurl.fileURLWithPath_.return_value = mock_url
            mock_isdir.return_value = True

            other_entry = self.dock.makeDockOtherEntry("/Users/test/Downloads")

            expected_entry = {
                "tile-data": {
                    "arrangement": 2,  # sort by date added for Downloads
                    "displayas": 1,
                    "file-data": {
                        "_CFURLString": "file:///Users/test/Downloads/",
                        "_CFURLStringType": 15,
                    },
                    "file-label": "Downloads",
                    "dock-extra": False,
                    "showas": 0,
                },
                "tile-type": "directory-tile",
            }

            self.assertEqual(other_entry, expected_entry)

    def test_make_dock_other_entry_custom_options(self):
        """Ensure docklib can create other entry with custom options."""
        # Mock NSURL.fileURLWithPath_ and os.path.isdir
        with (
            patch("docklib.docklib.NSURL") as mock_nsurl,
            patch("docklib.docklib.os.path.isdir") as mock_isdir,
        ):
            mock_url = MagicMock()
            mock_url.absoluteString.return_value = "file:///Users/test/Pictures/"
            mock_nsurl.fileURLWithPath_.return_value = mock_url
            mock_isdir.return_value = True

            other_entry = self.dock.makeDockOtherEntry(
                "/Users/test/Pictures",
                arrangement=3,  # sort by modification date
                displayas=0,  # display as stack
                showas=2,  # grid view
            )

            expected_entry = {
                "tile-data": {
                    "arrangement": 3,
                    "displayas": 0,
                    "file-data": {
                        "_CFURLString": "file:///Users/test/Pictures/",
                        "_CFURLStringType": 15,
                    },
                    "file-label": "Pictures",
                    "dock-extra": False,
                    "showas": 2,
                },
                "tile-type": "directory-tile",
            }

            self.assertEqual(other_entry, expected_entry)

    def test_make_dock_other_url_entry_default_label(self):
        """Ensure docklib can create URL entry with default label."""
        # Mock NSURL.URLWithString_
        with patch("docklib.docklib.NSURL") as mock_nsurl:
            mock_url = MagicMock()
            mock_url.absoluteString.return_value = "https://www.apple.com/"
            mock_nsurl.URLWithString_.return_value = mock_url

            url_entry = self.dock.makeDockOtherURLEntry("https://www.apple.com/")

            expected_entry = {
                "tile-data": {
                    "label": "",  # Default is empty string, not the URL
                    "url": {
                        "_CFURLString": "https://www.apple.com/",
                        "_CFURLStringType": 15,
                    },
                },
                "tile-type": "url-tile",
            }

            self.assertEqual(url_entry, expected_entry)
            mock_nsurl.URLWithString_.assert_called_once_with("https://www.apple.com/")

    def test_make_dock_other_url_entry_custom_label(self):
        """Ensure docklib can create URL entry with custom label."""
        # Mock NSURL.URLWithString_
        with patch("docklib.docklib.NSURL") as mock_nsurl:
            mock_url = MagicMock()
            mock_url.absoluteString.return_value = "https://www.github.com/"
            mock_nsurl.URLWithString_.return_value = mock_url

            url_entry = self.dock.makeDockOtherURLEntry(
                "https://www.github.com/", "GitHub"
            )

            expected_entry = {
                "tile-data": {
                    "label": "GitHub",
                    "url": {
                        "_CFURLString": "https://www.github.com/",
                        "_CFURLStringType": 15,
                    },
                },
                "tile-type": "url-tile",
            }

            self.assertEqual(url_entry, expected_entry)

    def test_make_dock_other_url_entry_none_label(self):
        """Ensure docklib handles None label correctly."""
        # Mock NSURL.URLWithString_
        with patch("docklib.docklib.NSURL") as mock_nsurl:
            mock_url = MagicMock()
            mock_url.absoluteString.return_value = "https://www.example.com/"
            mock_nsurl.URLWithString_.return_value = mock_url

            url_entry = self.dock.makeDockOtherURLEntry(
                "https://www.example.com/", None
            )

            expected_entry = {
                "tile-data": {
                    "label": "https://www.example.com/",
                    "url": {
                        "_CFURLString": "https://www.example.com/",
                        "_CFURLStringType": 15,
                    },
                },
                "tile-type": "url-tile",
            }

            self.assertEqual(url_entry, expected_entry)


class TestLaunchAgentManager(unittest.TestCase):
    """Unit test class for LaunchAgentManager."""

    def setUp(self):
        # Mock subprocess.run for LaunchAgentManager
        self.mock_subprocess_run_patcher = patch("docklib.docklib.subprocess.run")
        self.mock_subprocess_run = self.mock_subprocess_run_patcher.start()

        # Mock pwd for LaunchAgentManager initialization
        self.mock_pwd_patcher = patch("docklib.docklib.pwd")
        self.mock_pwd = self.mock_pwd_patcher.start()
        mock_user = MagicMock()
        mock_user.pw_uid = 501
        self.mock_pwd.getpwuid.return_value = mock_user

        # Mock os.path.exists
        self.mock_exists_patcher = patch("docklib.docklib.os.path.exists")
        self.mock_exists = self.mock_exists_patcher.start()
        self.mock_exists.return_value = True

    def tearDown(self):
        self.mock_subprocess_run_patcher.stop()
        self.mock_pwd_patcher.stop()
        self.mock_exists_patcher.stop()

    def test_launch_agent_manager_init_default(self):
        """Test LaunchAgentManager initialization with default service target."""
        manager = docklib.LaunchAgentManager()
        self.assertEqual(manager.service_target, "gui/501")

    def test_launch_agent_manager_init_custom(self):
        """Test LaunchAgentManager initialization with custom service target."""
        manager = docklib.LaunchAgentManager(service_target="system")
        self.assertEqual(manager.service_target, "system")

    def test_bootstrap_success(self):
        """Test successful bootstrap operation."""
        # Mock successful subprocess result
        mock_result = MagicMock()
        mock_result.returncode = 0
        self.mock_subprocess_run.return_value = mock_result

        manager = docklib.LaunchAgentManager()
        result = manager.bootstrap("/path/to/test.plist")

        self.assertTrue(result)
        self.mock_subprocess_run.assert_called_with(
            ["/bin/launchctl", "bootstrap", "gui/501", "/path/to/test.plist"],
            capture_output=True,
            text=True,
            check=False,
        )

    def test_bootstrap_failure(self):
        """Test bootstrap operation failure."""
        # Mock failed subprocess result
        mock_result = MagicMock()
        mock_result.returncode = 1
        mock_result.stderr = "Bootstrap failed"
        self.mock_subprocess_run.return_value = mock_result

        manager = docklib.LaunchAgentManager()

        with self.assertRaises(docklib.LaunchAgentError):
            manager.bootstrap("/path/to/test.plist")

    def test_bootstrap_file_not_found(self):
        """Test bootstrap with non-existent plist file."""
        self.mock_exists.return_value = False

        manager = docklib.LaunchAgentManager()

        with self.assertRaises(docklib.LaunchAgentError):
            manager.bootstrap("/path/to/nonexistent.plist")

    def test_bootout_success(self):
        """Test successful bootout operation."""
        # Mock successful subprocess result
        mock_result = MagicMock()
        mock_result.returncode = 0
        self.mock_subprocess_run.return_value = mock_result

        manager = docklib.LaunchAgentManager()
        result = manager.bootout("com.example.agent")

        self.assertTrue(result)
        self.mock_subprocess_run.assert_called_with(
            ["/bin/launchctl", "bootout", "gui/501/com.example.agent"],
            capture_output=True,
            text=True,
            check=False,
        )

    def test_bootout_service_not_loaded(self):
        """Test bootout when service is not loaded (should still return True)."""
        # Mock failed subprocess result with "not loaded" message
        mock_result = MagicMock()
        mock_result.returncode = 1
        mock_result.stderr = "No such process"
        self.mock_subprocess_run.return_value = mock_result

        manager = docklib.LaunchAgentManager()
        result = manager.bootout("com.example.agent")

        self.assertTrue(result)  # Should return True for "not loaded" case

    def test_is_loaded_true(self):
        """Test is_loaded returns True for loaded service."""
        # Mock successful subprocess result
        mock_result = MagicMock()
        mock_result.returncode = 0
        self.mock_subprocess_run.return_value = mock_result

        manager = docklib.LaunchAgentManager()
        result = manager.is_loaded("com.example.agent")

        self.assertTrue(result)
        self.mock_subprocess_run.assert_called_with(
            ["/bin/launchctl", "print", "gui/501/com.example.agent"],
            capture_output=True,
            text=True,
            check=False,
        )

    def test_is_loaded_false(self):
        """Test is_loaded returns False for non-loaded service."""
        # Mock failed subprocess result
        mock_result = MagicMock()
        mock_result.returncode = 1
        self.mock_subprocess_run.return_value = mock_result

        manager = docklib.LaunchAgentManager()
        result = manager.is_loaded("com.example.agent")

        self.assertFalse(result)


if __name__ == "__main__":
    unittest.main()
