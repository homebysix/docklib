# pylint: disable=C0103

"""Python module intended to assist IT administrators with manipulation of the macOS Dock.

See project details on GitHub: https://github.com/homebysix/docklib
"""

import logging
import os
import pwd
import subprocess
from urllib.parse import unquote, urlparse
from typing import Optional

# pylint: disable=E0611
from Foundation import (
    NSURL,
    CFPreferencesAppSynchronize,
    CFPreferencesCopyAppValue,
    CFPreferencesSetAppValue,
)

# pylint: enable=E0611

# Configure logging
logging.basicConfig(
    level=logging.WARNING, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class DockError(Exception):
    """Basic exception."""

    pass


class LaunchAgentError(Exception):
    """Exception raised for LaunchAgent operations."""

    pass


class LaunchAgentManager:
    """Class to handle macOS LaunchAgent operations using modern launchctl commands."""

    def __init__(self, service_target: Optional[str] = None) -> None:
        """Initialize the LaunchAgentManager."""

        if service_target is None:
            # Get current user ID for GUI domain
            uid = pwd.getpwuid(os.getuid()).pw_uid
            self.service_target = f"gui/{uid}"
        else:
            self.service_target = service_target

    def bootstrap(self, plist_path: str) -> bool:
        """Load a LaunchAgent using bootstrap command."""

        if not os.path.exists(plist_path):
            raise LaunchAgentError(f"LaunchAgent plist not found: {plist_path}")

        cmd = ["/bin/launchctl", "bootstrap", self.service_target, plist_path]
        logger.debug(f"Executing bootstrap command: {' '.join(cmd)}")

        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=False)
            logger.debug(
                f"Bootstrap command result: returncode={result.returncode}, "
                f"stdout='{result.stdout.strip()}', stderr='{result.stderr.strip()}'"
            )

            if result.returncode == 0:
                logger.info(f"Successfully bootstrapped LaunchAgent: {plist_path}")
                return True
            raise LaunchAgentError(
                f"Failed to bootstrap {plist_path}: {result.stderr.strip()}"
            )
        except subprocess.SubprocessError as e:
            raise LaunchAgentError(f"Subprocess error during bootstrap: {e}") from e

    def bootout(self, service_name: str) -> bool:
        """Unload a LaunchAgent using bootout command."""

        cmd = ["/bin/launchctl", "bootout", f"{self.service_target}/{service_name}"]
        logger.debug(f"Executing bootout command: {' '.join(cmd)}")

        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=False)
            logger.debug(
                f"Bootout command result: returncode={result.returncode}, "
                f"stdout='{result.stdout.strip()}', stderr='{result.stderr.strip()}'"
            )

            if result.returncode == 0:
                logger.info(f"Successfully booted out LaunchAgent: {service_name}")
                return True
            # Service might not be loaded, which is not necessarily an error
            if (
                "No such process" in result.stderr
                or "Could not find service" in result.stderr
            ):
                logger.info(
                    f"LaunchAgent {service_name} was not loaded (bootout successful)"
                )
                return True
            raise LaunchAgentError(
                f"Failed to bootout {service_name}: {result.stderr.strip()}"
            )
        except subprocess.SubprocessError as e:
            raise LaunchAgentError(f"Subprocess error during bootout: {e}") from e

    def is_loaded(self, service_name: str) -> bool:
        """Check if a service is currently loaded."""

        cmd = ["/bin/launchctl", "print", f"{self.service_target}/{service_name}"]
        logger.debug(f"Executing is_loaded check command: {' '.join(cmd)}")

        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=False)
            logger.debug(
                f"Is_loaded command result: returncode={result.returncode}, "
                f"stdout='{result.stdout.strip()}', stderr='{result.stderr.strip()}'"
            )
            is_loaded = result.returncode == 0
            logger.debug(f"LaunchAgent {service_name} loaded status: {is_loaded}")
            return is_loaded
        except subprocess.SubprocessError:
            logger.debug(
                f"Subprocess error checking if {service_name} is loaded, returning False"
            )
            return False


class Dock:
    """Class to handle Dock operations."""

    _DOMAIN = "com.apple.dock"
    _DOCK_PLIST = os.path.expanduser("~/Library/Preferences/com.apple.dock.plist")
    _DOCK_LAUNCHAGENT_ID = "com.apple.Dock.agent"
    _DOCK_LAUNCHAGENT_FILE = "/System/Library/LaunchAgents/com.apple.Dock.plist"
    # TODO: static-apps and static-others
    _SECTIONS = ["persistent-apps", "persistent-others"]
    _MUTABLE_KEYS = [
        "autohide",
        "autohide-immutable",
        "contents-immutable",
        "dblclickbehavior",
        "largesize",
        "launchanim",
        "launchanim-immutable",
        "magnification",
        "magnification-immutable",
        "magsize-immutable",
        "mineffect",
        "mineffect-immutable",
        "minimize-to-application",
        "minimize-to-application-immutable",
        "orientation",
        "orientation-immutable",
        "position-immutable",
        "tilesize",
        "show-process-indicators",
        "show-progress-indicators",
        "show-recents",
        "show-recents-immutable",
        "size-immutable",
        "windowtabbing",
        "AllowDockFixupOverride",
    ]

    _IMMUTABLE_KEYS = ["mod-count", "recent-apps", "trash-full"]

    items: dict = {}

    def __init__(self) -> None:
        for key in self._SECTIONS:
            try:
                section = CFPreferencesCopyAppValue(key, self._DOMAIN)
                self.items[key] = section.mutableCopy() if section else None
            except Exception:
                raise
        for key in self._MUTABLE_KEYS + self._IMMUTABLE_KEYS:
            try:
                value = CFPreferencesCopyAppValue(key, self._DOMAIN)
                setattr(self, key.replace("-", "_"), value)
            except Exception:
                raise

    def save(self) -> None:
        """Saves our (modified) Dock preferences."""

        # Create LaunchAgent manager for current user's GUI domain
        agent = LaunchAgentManager()

        # unload Dock launchd job so we can make our changes unmolested
        agent.bootout(self._DOCK_LAUNCHAGENT_ID)

        for key in self._SECTIONS:
            try:
                CFPreferencesSetAppValue(key, self.items[key], self._DOMAIN)
            except Exception as exc:
                raise DockError from exc
        for key in self._MUTABLE_KEYS:
            # Python doesn't support hyphens in attribute names, so convert
            # to/from underscores as needed.
            if getattr(self, key.replace("-", "_")) is not None:
                try:
                    CFPreferencesSetAppValue(
                        key.replace("_", "-"),
                        getattr(self, key.replace("-", "_")),
                        self._DOMAIN,
                    )
                except Exception as exc:
                    raise DockError from exc
        if not CFPreferencesAppSynchronize(self._DOMAIN):
            raise DockError

        # restart the Dock
        agent.bootstrap(self._DOCK_LAUNCHAGENT_FILE)

    def findExistingEntry(
        self, match_str: str, match_on: str = "any", section: str = "persistent-apps"
    ) -> int:
        """Returns index of a Dock item identified by match_str or -1 if no item
        is found.

        match_on values:
            label: match dock items with this file-label or label
                (e.g. Safari)
                NOTE: Labels can vary depending on the user's selected language.
            path: match dock items with this path on disk
                (e.g. /System/Applications/Safari.app)
            name_ext: match dock items with this file/folder basename
                (e.g. Safari.app)
            name_noext: match dock items with this basename, without extension
                (e.g. Safari)
            any: Try all the criteria above in order, and return the first result.
        """
        logger.debug(
            f"Searching for Dock entry: match_str='{match_str}', "
            f"match_on='{match_on}', section='{section}'"
        )

        section_items = self.items[section]
        if section_items:
            logger.debug(f"Found {len(section_items)} items in {section} section")
            # Determine the order of attributes to match on.
            if match_on == "any":
                match_ons = ["label", "path", "name_ext", "name_noext"]
            else:
                match_ons = [match_on]

            # Iterate through match criteria (ensures a full scan of the Dock
            # for each criterion, if matching on "any").
            for m in match_ons:
                logger.debug(f"Searching using match criterion: {m}")
                # Iterate through items in section
                for index, item in enumerate(section_items):
                    url = item["tile-data"].get("file-data", {}).get("_CFURLString", "")
                    path = unquote(urlparse(url.rstrip("/")).path)
                    name_ext = os.path.basename(path)
                    name_noext = os.path.splitext(name_ext)[0]

                    if m == "label":
                        # Most dock items use "file-label", but URLs use "label"
                        for label_key in ("file-label", "label"):
                            if item["tile-data"].get(label_key) == match_str:
                                logger.debug(
                                    f"Found match at index {index} using {m} criterion "
                                    f"(label_key='{label_key}')"
                                )
                                return index
                    elif m == "path" and path == match_str:
                        logger.debug(
                            f"Found match at index {index} using {m} criterion"
                        )
                        return index
                    elif m == "name_ext" and name_ext == match_str:
                        logger.debug(
                            f"Found match at index {index} using {m} criterion"
                        )
                        return index
                    elif m == "name_noext" and name_noext == match_str:
                        logger.debug(
                            f"Found match at index {index} using {m} criterion"
                        )
                        return index
        else:
            logger.debug(f"No items found in {section} section")

        logger.debug(f"No match found for '{match_str}' in {section} section")
        return -1

    def findExistingLabel(
        self, match_str: str, section: str = "persistent-apps"
    ) -> int:
        """Points to findExistingEntry, maintained for compatibility."""
        return self.findExistingEntry(match_str, match_on="label", section=section)

    def findExistingURL(self, match_url: str) -> int:
        """Returns index of item with URL matching match_url or -1 if not
        found."""
        logger.debug(f"Searching for Dock URL entry: match_url='{match_url}'")

        section_items = self.items["persistent-others"]
        if section_items:
            logger.debug(
                f"Found {len(section_items)} items in persistent-others section"
            )
            for index, item in enumerate(section_items):
                if item["tile-data"].get("url"):
                    if item["tile-data"]["url"]["_CFURLString"] == match_url:
                        logger.debug(f"Found URL match at index {index}")
                        return index
        else:
            logger.debug("No items found in persistent-others section")

        logger.debug(f"No URL match found for '{match_url}'")
        return -1

    def removeDockEntry(
        self, match_str: str, match_on: str = "any", section: str = ""
    ) -> None:
        """Removes a Dock entry identified by "match_str", if any. Defaults to
        matching "match_str" by the "any" criteria order listed in the
        findExistingEntry docstring."""
        if section:
            sections = [section]
        else:
            sections = self._SECTIONS

        removed_count = 0
        for sect in sections:
            found_index = self.findExistingEntry(
                match_str, match_on=match_on, section=sect
            )
            if found_index > -1:
                del self.items[sect][found_index]
                removed_count += 1
                logger.info(
                    f"Removed Dock entry '{match_str}' from {sect} section at index {found_index}"
                )

        if removed_count == 0:
            logger.info(f"No Dock entry found to remove for '{match_str}'")

    def removeDockURLEntry(self, url: str) -> None:
        """Removes a Dock entry with matching url, if any."""
        found_index = self.findExistingURL(url)
        if found_index > -1:
            del self.items["persistent-others"][found_index]
            logger.info(
                f"Removed Dock URL entry '{url}' from persistent-others section at index {found_index}"
            )
        else:
            logger.info(f"No Dock URL entry found to remove for '{url}'")

    def replaceDockEntry(
        self,
        newpath: str,
        match_str: str = "",
        match_on: str = "any",
        label: str = "",  # deprecated
        section: str = "persistent-apps",
    ) -> None:
        """Replaces a Dock entry.

        If match_str is provided, it will be used to match the item to be replaced.
        See the findExistingEntry function docstring for possible "match_on" values.

        If match_str is not provided, the item to be replaced will be derived from
        the newpath filename, without extension.

        The "label" parameter is deprecated in favor of match_str and will be
        removed someday.
        """
        if section == "persistent-apps":
            newitem = self.makeDockAppEntry(newpath)
        else:
            newitem = self.makeDockOtherEntry(newpath)
        if not newitem:
            return
        if label:
            print(
                "WARNING: The label parameter is deprecated. Use match_str instead. "
                "Details: https://github.com/homebysix/docklib/issues/32"
            )
            match_str = label
            match_on = "label"
        if not match_str:
            match_str = os.path.splitext(os.path.basename(newpath))[0]
        found_index = self.findExistingEntry(
            match_str, match_on=match_on, section=section
        )
        if found_index > -1:
            self.items[section][found_index] = newitem
            logger.info(
                f"Replaced Dock entry '{match_str}' with '{newpath}' in {section} section at index {found_index}"
            )
        else:
            logger.info(f"No existing Dock entry found to replace for '{match_str}'")

    def makeDockAppSpacer(self, tile_type: str = "spacer-tile") -> dict:
        """Makes an empty space in the Dock."""
        if tile_type not in ["spacer-tile", "small-spacer-tile"]:
            msg = f"{tile_type}: invalid makeDockAppSpacer type."
            raise ValueError(msg)
        result = {"tile-data": {}, "tile-type": tile_type}

        return result

    def makeDockAppEntry(self, thePath: str, label_name: str = "") -> dict:
        """Returns a dictionary corresponding to a Dock application item."""
        if not label_name:
            label_name = os.path.splitext(os.path.basename(thePath))[0]
        ns_url = NSURL.fileURLWithPath_(thePath).absoluteString()
        result = {
            "tile-data": {
                "file-data": {"_CFURLString": ns_url, "_CFURLStringType": 15},
                "file-label": label_name,
                "file-type": 41,
            },
            "tile-type": "file-tile",
        }

        return result

    def makeDockOtherEntry(
        self, thePath: str, arrangement: int = 0, displayas: int = 1, showas: int = 0
    ) -> dict:
        """Returns a dictionary corresponding to a Dock folder or file item.

        arrangement values:
            1: sort by name
            2: sort by date added
            3: sort by modification date
            4: sort by creation date
            5: sort by kind
        displayas values:
            0: display as stack
            1: display as folder
        showas values:
            0: auto
            1: fan
            2: grid
            3: list
        """

        label_name = os.path.splitext(os.path.basename(thePath))[0]
        if arrangement == 0:
            if label_name == "Downloads":
                # set to sort by date added
                arrangement = 2
            else:
                # set to sort by name
                arrangement = 1
        ns_url = NSURL.fileURLWithPath_(thePath).absoluteString()
        if os.path.isdir(thePath):
            result = {
                "tile-data": {
                    "arrangement": arrangement,
                    "displayas": displayas,
                    "file-data": {"_CFURLString": ns_url, "_CFURLStringType": 15},
                    "file-label": label_name,
                    "dock-extra": False,
                    "showas": showas,
                },
                "tile-type": "directory-tile",
            }
        else:
            result = {
                "tile-data": {
                    "file-data": {"_CFURLString": ns_url, "_CFURLStringType": 15},
                    "file-label": label_name,
                    "dock-extra": False,
                },
                "tile-type": "file-tile",
            }

        return result

    def makeDockOtherURLEntry(self, theURL: str, label: str = "") -> dict:
        """Returns a dictionary corresponding to a URL."""
        if label is None:
            label_name = str(theURL)
        else:
            label_name = label
        ns_url = NSURL.URLWithString_(theURL).absoluteString()
        result = {
            "tile-data": {
                "label": label_name,
                "url": {"_CFURLString": ns_url, "_CFURLStringType": 15},
            },
            "tile-type": "url-tile",
        }

        return result
