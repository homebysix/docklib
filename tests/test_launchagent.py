"""test_launchagent.py

Tests for LaunchAgentManager functionality.
"""

import unittest
from unittest.mock import patch, MagicMock

import docklib


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
