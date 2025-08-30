"""test_base.py

Base test class for docklib tests. Contains common setup/teardown and basic tests.
"""

import os
import pwd
import types
import unittest
from unittest.mock import patch, MagicMock

import docklib


class BaseDocklibTest(unittest.TestCase):
    """Base test class with common setup and teardown for all docklib tests."""

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


class TestDockBasics(BaseDocklibTest):
    """Basic Dock initialization and import tests."""

    def test_import(self):
        """Tests that the docklib module can be imported."""
        import docklib  # pylint: disable=import-outside-toplevel

        self.assertTrue(docklib)

    def test_init(self):
        """Tests that a Dock object can be initialized."""
        dock = docklib.Dock()
        self.assertIsInstance(dock, docklib.Dock)

    def test_sections(self):
        """Test that the expected sections are returned in the items dict."""
        dock = docklib.Dock()
        self.assertIn("persistent-apps", dock.items)
        self.assertIn("persistent-others", dock.items)

    def test_item_keys(self):
        """Test that the expected keys are present in dock items."""
        expected_keys = ["tile-type", "tile-data"]
        for item in self.dock.items["persistent-apps"]:
            for key in expected_keys:
                self.assertIn(key, item)
        for item in self.dock.items["persistent-others"]:
            for key in expected_keys:
                self.assertIn(key, item)

    def test_tile_data_keys(self):
        """Test that expected tile-data keys are present."""
        expected_app_keys = [
            "file-label",
            "file-data",
        ]
        for item in self.dock.items["persistent-apps"]:
            for key in expected_app_keys:
                self.assertIn(key, item["tile-data"])

        expected_other_keys = [
            "file-label",
            "file-data",
        ]
        for item in self.dock.items["persistent-others"]:
            for key in expected_other_keys:
                self.assertIn(key, item["tile-data"])

    def test_tile_types(self):
        """Test that expected tile-types are correct."""
        for item in self.dock.items["persistent-apps"]:
            self.assertEqual(item["tile-type"], "file-tile")
        for item in self.dock.items["persistent-others"]:
            self.assertIn(item["tile-type"], ["file-tile", "directory-tile"])
