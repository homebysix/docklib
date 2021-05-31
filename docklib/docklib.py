# -*- coding: utf-8 -*-

# pylint: disable=C0103

"""Python module intended to assist IT administrators with manipulation of the macOS Dock.

See project details on GitHub: https://github.com/homebysix/docklib
"""

import os
import subprocess
from distutils.version import LooseVersion
from platform import mac_ver

try:
    # Python 3
    from urllib.parse import unquote, urlparse
except ImportError:
    # Python 2
    from urllib import unquote

    from urlparse import urlparse


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
    # TODO: static-apps and static-others
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
            # Python doesn't support hyphens in attribute names, so convert
            # to/from underscores as needed.
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

    def findExistingEntry(self, match_str, match_on="any", section="persistent-apps"):
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
        section_items = self.items[section]
        if section_items:
            # Determine the order of attributes to match on.
            if match_on == "any":
                match_ons = ["label", "path", "name_ext", "name_noext"]
            else:
                match_ons = [match_on]

            # Iterate through match criteria (ensures a full scan of the Dock
            # for each criterion, if matching on "any").
            for m in match_ons:
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
                                return index
                    elif m == "path" and path == match_str:
                        return index
                    elif m == "name_ext" and name_ext == match_str:
                        return index
                    elif m == "name_noext" and name_noext == match_str:
                        return index

        return -1

    def findExistingLabel(self, match_str, section="persistent-apps"):
        """Points to findExistingEntry, maintained for compatibility."""
        return self.findExistingEntry(match_str, match_on="label", section=section)

    def findExistingURL(self, match_url):
        """Returns index of item with URL matching match_url or -1 if not
        found."""
        section_items = self.items["persistent-others"]
        if section_items:
            for index, item in enumerate(section_items):
                if item["tile-data"].get("url"):
                    if item["tile-data"]["url"]["_CFURLString"] == match_url:
                        return index

        return -1

    def removeDockEntry(self, match_str, match_on="any", section=None):
        """Removes a Dock entry identified by "match_str", if any. Defaults to
        matching "match_str" by the "any" criteria order listed in the
        findExistingEntry docstring."""
        if section:
            sections = [section]
        else:
            sections = self._SECTIONS
        for sect in sections:
            found_index = self.findExistingEntry(
                match_str, match_on=match_on, section=sect
            )
            if found_index > -1:
                del self.items[sect][found_index]

    def removeDockURLEntry(self, url):
        """Removes a Dock entry with matching url, if any."""
        found_index = self.findExistingURL(url)
        if found_index > -1:
            del self.items["persistent-others"][found_index]

    def replaceDockEntry(
        self,
        newpath,
        match_str=None,
        match_on="any",
        label=None,  # deprecated
        section="persistent-apps",
    ):
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
