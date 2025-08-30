"""test_dock_make.py

Tests for Dock item creation methods (make* functions).
"""

from unittest.mock import patch, MagicMock

from tests.test_base import BaseDocklibTest


class TestDockMakers(BaseDocklibTest):
    """Tests for Dock item creation methods."""

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
