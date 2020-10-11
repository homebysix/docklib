# -*- coding: utf-8 -*-

# pylint: disable=C0103

"""Python module intended to assist IT administrators with manipulation of the macOS Dock."""

import os
import subprocess
from distutils.version import LooseVersion
from platform import mac_ver

# pylint: disable=E0611
from Foundation import (
    NSURL,
    CFPreferencesAppSynchronize,
    CFPreferencesCopyAppValue,
    CFPreferencesSetAppValue,
)


# pylint: enable=E0611


class DockError(Exception):
    """Basic exception."""

    pass


class Dock:
    """Class to handle Dock operations."""

    _DOMAIN = "com.apple.dock"
    _DOCK_PLIST = os.path.expanduser("~/Library/Preferences/com.apple.dock.plist")
    _DOCK_LAUNCHAGENT_ID = "com.apple.Dock.agent"
    _DOCK_LAUNCHAGENT_FILE = "/System/Library/LaunchAgents/com.apple.Dock.plist"
    _SECTIONS = ["persistent-apps", "persistent-others"]
    _MUTABLE_KEYS = [
        "autohide",
        "orientation",
        "tilesize",
        "largesize",
        "orientation-immutable",
        "position-immutable",
        "autohide-immutable",
        "magnification",
        "magnification-immutable",
        "magsize-immutable",
        "show-progress-indicators",
        "contents-immutable",
        "size-immutable",
        "mineffect",
        "mineffect-immutable",
        "size-immutable",
        "minimize-to-application",
        "minimize-to-application-immutable",
        "show-process-indicators",
        "launchanim",
        "launchanim-immutable",
    ]

    _IMMUTABLE_KEYS = ["mod-count", "trash-full"]
    if LooseVersion(mac_ver()[0]) >= LooseVersion("10.12"):
        _MUTABLE_KEYS.append("AllowDockFixupOverride")
    if LooseVersion(mac_ver()[0]) >= LooseVersion("10.14"):
        _MUTABLE_KEYS.append("show-recents")
        _IMMUTABLE_KEYS.append("recent-apps")
    if LooseVersion(mac_ver()[0]) >= LooseVersion("10.15"):
        _MUTABLE_KEYS.extend(
            ["dblclickbehavior", "show-recents-immutable", "windowtabbing"]
        )

    items = {}

    def __init__(self):
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

    def save(self):
        """Saves our (modified) Dock preferences."""
        # unload Dock launchd job so we can make our changes unmolested
        subprocess.call(["/bin/launchctl", "unload", self._DOCK_LAUNCHAGENT_FILE])

        for key in self._SECTIONS:
            try:
                CFPreferencesSetAppValue(key, self.items[key], self._DOMAIN)
            except Exception:
                raise DockError
        for key in self._MUTABLE_KEYS:
            if getattr(self, key.replace("-", "_")) is not None:
                try:
                    CFPreferencesSetAppValue(
                        key.replace("_", "-"),
                        getattr(self, key.replace("-", "_")),
                        self._DOMAIN,
                    )
                except Exception:
                    raise DockError
        if not CFPreferencesAppSynchronize(self._DOMAIN):
            raise DockError

        # restart the Dock
        subprocess.call(["/bin/launchctl", "load", self._DOCK_LAUNCHAGENT_FILE])
        subprocess.call(["/bin/launchctl", "start", self._DOCK_LAUNCHAGENT_ID])

    def findExistingLabel(self, test_label, section="persistent-apps"):
        """Returns index of item with label matching test_label or -1 if not
        found."""
        section_items = self.items[section]
        if section_items:
            for index, item in enumerate(section_items):
                if item["tile-data"].get("file-label") == test_label:
                    return index

        return -1

    def removeDockEntry(self, label, section=None):
        """Removes a Dock entry with matching label, if any."""
        if section:
            sections = [section]
        else:
            sections = self._SECTIONS
        for sect in sections:
            found_index = self.findExistingLabel(label, section=sect)
            if found_index > -1:
                del self.items[sect][found_index]

    def replaceDockEntry(self, thePath, label=None, section="persistent-apps"):
        """Replaces a Dock entry.

        If label is None, then a label is derived from the item path.
        The new entry replaces an entry with the given or derived label
        """
        if section == "persistent-apps":
            new_item = self.makeDockAppEntry(thePath)
        else:
            new_item = self.makeDockOtherEntry(thePath)
        if new_item:
            if not label:
                label = os.path.splitext(os.path.basename(thePath))[0]
            found_index = self.findExistingLabel(label, section=section)
            if found_index > -1:
                self.items[section][found_index] = new_item

    def makeDockAppSpacer(self, type="spacer-tile"):
        """Makes an empty space in the Dock."""
        if type not in ["spacer-tile", "small-spacer-tile"]:
            msg = "{0}: invalid makeDockAppSpacer type.".format(type)
            raise ValueError(msg)
        result = {"tile-data": {}, "tile-type": type}

        return result

    def makeDockAppEntry(self, thePath, label_name=None):
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

    def makeDockOtherEntry(self, thePath, arrangement=0, displayas=1, showas=0):
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

    def makeDockOtherURLEntry(self, theURL, label=None):
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
