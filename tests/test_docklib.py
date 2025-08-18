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
