# docklib

This is a Python module intended to assist IT administrators with manipulation of the macOS Dock.

Originally created as a [Gist](https://gist.github.com/gregneagle/5c422d709c93615341a21009f800222e) by @gregneagle, this fork has been modified to include support for some additional Dock features, and has been packaged for multiple distribution options.

## docklib or dockutil?

The very capable [dockutil](https://github.com/kcrawford/dockutil) tool serves a similar function to docklib. Why would Mac admins choose one over the other?

The primary benefit of **docklib** is that it allows the Dock to be manipulated in a "Pythonic" way. By parsing the Dock configuration into an object with attributes and data structures that can be modified using familiar functions like `.append()` and `.insert()`, docklib aims to make Python scripters feel at home.

In contrast, **dockutil** behaves more like a shell command-line utility. This makes dockutil a good choice if you're more comfortable writing user setup scripts in bash or zsh. Dockutil also has an `--allhomes` argument that allows Dock configuration for all users to be modified at the same time. Docklib isn't designed for this, instead focusing on configuring the Dock for the user that is currently logged in (for example, via an [outset](https://github.com/chilcote/outset) `login-once` or `login-every` script). [Here's](https://appleshare.it/posts/use-dockutil-in-a-script/) a great article to get you started with dockutil, if that sounds like what you're after.

## Installation

There are multiple methods of installing docklib, depending on how you plan to use it.

### Package installer

You can use the included __build_pkg.sh__ script to build a macOS installer .pkg file. You can use this package to install docklib on your own Mac, or deploy the package using a tool like Jamf or Munki to install docklib on managed devices.

To run the script, `cd` to a local clone of this repository, then run:

```
./build_pkg.sh
```

The resulting pkg will be built in a temporary folder and shown in the Finder.

__NOTE__: The default install destination is __/Library/Python/2.7/site-packages/docklib__, which makes docklib available to the built-in macOS Python 2.7 framework. If you leverage a different Python installation, you'll need to modify this path in the __build_pkg.sh__ script prior to building the installer package.

### Pip

Docklib has been published to PyPI in order to make it available for installation using pip.

```
pip install docklib
```

This method is not intended to be used directly on managed devices, but it could be leveraged alongside a custom Python framework (like one built with [macadmins/python](https://github.com/macadmins/python) or [relocatable-python](https://github.com/gregneagle/relocatable-python)) using a requirements file.

### Managed Python

Docklib is included in the "recommended" flavor of the [macadmins/python](https://github.com/macadmins/python) release package. Installing this package and using `#!/usr/local/managed_python3` for your docklib script shebang may be the most self-contained and future-proof way to deploy docklib.

### Manual

Another method of using docklib is to simply place the docklib.py file in the same location as the Python script(s) you use to manipulate the macOS dock. Some examples of such scripts are included below.

## Examples

### Add Microsoft Word to the right side of the Dock

```python
from docklib import Dock

dock = Dock()
item = dock.makeDockAppEntry("/Applications/Microsoft Word.app")
dock.items["persistent-apps"].append(item)
dock.save()
```

### Add Microsoft Word to the left side of the Dock

```python
from docklib import Dock

dock = Dock()
item = dock.makeDockAppEntry("/Applications/Microsoft Word.app")
dock.items["persistent-apps"] = [item] + dock.items["persistent-apps"]
dock.save()
```

### Replace Mail.app with Outlook in the Dock

```python
from docklib import Dock

dock = Dock()
dock.replaceDockEntry("/Applications/Microsoft Outlook.app", "Mail")
dock.save()
```

### Remove Calendar from the Dock

```python
from docklib import Dock

dock = Dock()
dock.removeDockEntry("Calendar")
dock.save()
```

### Display the current orientation of the Dock

```python
from docklib import Dock

dock = Dock()
print(dock.orientation)
```

### Make the Dock display on the left, and enable autohide

```python
from docklib import Dock

dock = Dock()
dock.orientation = "left"
dock.autohide = True
dock.save()
```

### Add the Documents folder to the right side of the Dock

Displays as a stack to the right of the Dock divider, sorted by modification date, that expands into a fan when clicked. This example checks for the existence of the Documents item and only adds it if it's not already present.

```python
import os
from docklib import Dock

dock = Dock()
if dock.findExistingEntry("Documents", section="persistent-others") == -1:
    item = dock.makeDockOtherEntry(
        os.path.expanduser("~/Documents"), arrangement=3, displayas=1, showas=1
    )
    dock.items["persistent-others"] = [item] + dock.items["persistent-others"]
    dock.save()
```
### Add a URL to the right side of the Dock

Displays as a globe to the right of the Dock divider, that launches a URL in the default browser when clicked. This example checks for the existence of the Documents item and only adds it if it's not already present.

```python
import os
from docklib import Dock

dock = Dock()
if dock.findExistingEntry("GitHub", section="persistent-others") == -1:
    item = dock.makeDockOtherURLEntry("https://www.github.com/", label="GitHub")
    dock.items["persistent-others"] = [item] + dock.items["persistent-others"]
    dock.save()
```

### Specify a custom Dock for the local IT technician account

```python
import os
from docklib import Dock

tech_dock = [
    "/Applications/Google Chrome.app",
    "/Applications/App Store.app",
    "/Applications/Managed Software Center.app",
    "/Applications/System Preferences.app",
    "/Applications/Utilities/Activity Monitor.app",
    "/Applications/Utilities/Console.app",
    "/Applications/Utilities/Disk Utility.app",
    "/Applications/Utilities/Migration Assistant.app",
    "/Applications/Utilities/Terminal.app",
]
dock = Dock()
dock.items["persistent-apps"] = []
for item in tech_dock:
    if os.path.exists(item):
        item = dock.makeDockAppEntry(item)
        dock.items["persistent-apps"].append(item)
dock.save()
```

Or if you prefer using a [list comprehension](https://www.pythonforbeginners.com/basics/list-comprehensions-in-python):

```python
import os
from docklib import Dock

tech_dock = [
    "/Applications/Google Chrome.app",
    "/Applications/App Store.app",
    "/Applications/Managed Software Center.app",
    "/Applications/System Preferences.app",
    "/Applications/Utilities/Activity Monitor.app",
    "/Applications/Utilities/Console.app",
    "/Applications/Utilities/Disk Utility.app",
    "/Applications/Utilities/Migration Assistant.app",
    "/Applications/Utilities/Terminal.app",
]
dock = Dock()
dock.items["persistent-apps"] = [
    dock.makeDockAppEntry(item) for item in tech_dock if os.path.exists(item)
]
dock.save()
```

## More information

For more examples and tips for creating your docklib script, see my guides on:

- [Writing Resilient Docklib Scripts](https://www.elliotjordan.com/posts/resilient-docklib/)
- [Deploying and running docklib scripts using Outset](https://www.elliotjordan.com/posts/docklib-outset/)
