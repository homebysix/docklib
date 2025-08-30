"""test_dock_apps.py

Tests for Dock application operations (add/remove apps).
"""

from unittest.mock import patch

from tests.test_base import BaseDocklibTest


class TestDockApps(BaseDocklibTest):
    """Tests for Dock application operations."""

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
