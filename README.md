# docklib

This is a Python module intended to assist IT administrators with manipulation of the macOS Dock.

Originally created as a [Gist](https://gist.github.com/gregneagle/5c422d709c93615341a21009f800222e) by @gregneagle, this fork has been modified to include support for some additional Dock features, and has been packaged for multiple distribution options.

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

This method is not intended to be used directly on managed devices, but it could be leveraged alongside a custom Python framework (like one build with [macadmins/python](https://github.com/macadmins/python) or [relocatable-python](https://github.com/gregneagle/relocatable-python)) using a requirements file.

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
print dock.orientation
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
if dock.findExistingLabel("Documents", section="persistent-others") == -1:
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
if dock.findExistingLabel("GitHub", section="persistent-others") == -1:
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
