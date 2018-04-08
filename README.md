# docklib

This is a Python module intended to assist IT administrators with manipulation of the macOS Dock.

Originally created as a [Gist](https://gist.github.com/gregneagle/5c422d709c93615341a21009f800222e) by @gregneagle and [modified](https://gist.github.com/discentem/448b3f99b98ebabdcb56a55c40076449) to include support for spacers by @discentem.

## Installation

Place the docklib.py file in your Python path so its contents can be imported into scripts you create. Or, include the file in the same directory as your script.

## Examples

### Add Microsoft Word to the right side of the Dock

```python
from docklib import Dock
dock = Dock()
item = dock.makeDockAppEntry('/Applications/Microsoft Word.app')
dock.items['persistent-apps'].append(item)
dock.save()
```

### Add Microsoft Word to the left side of the Dock

```python
from docklib import Dock
dock = Dock()
item = dock.makeDockAppEntry('/Applications/Microsoft Word.app')
dock.items['persistent-apps'] = [item] + dock.items['persistent-apps']
dock.save()
```

### Replace Mail.app with Outlook in the Dock

```python
from docklib import Dock
dock = Dock()
item = dock.replaceDockEntry('/Applications/Microsoft Outlook.app', 'Mail')
dock.save()
```

### Remove Calendar from the Dock

```python
from docklib import Dock
dock = Dock()
item = dock.removeDockEntry('Calendar')
dock.save()
```

### Add the Documents folder to the right side of the Dock

Displays as a stack to the right of the Dock divider, sorted by modification date, that expands into a fan when clicked. This example checks for the existence of the Documents item and only adds it if it's not already present.

```python
import os
from docklib import Dock
dock = Dock()
if dock.findExistingLabel('Documents', section='persistent-others') == -1:
    item = dock.makeDockOtherEntry(os.path.expanduser('~/Documents'),
                                   arrangement=3,
                                   displayas=1,
                                   showas=1)
    dock.items['persistent-others'] = [item] + dock.items['persistent-others']
    dock.save()
```

### Specify a custom Dock for the local IT technician account

```python
import os
from docklib import Dock
tech_dock = [
    '/Applications/Google Chrome.app',
    '/Applications/App Store.app',
    '/Applications/Managed Software Center.app',
    '/Applications/System Preferences.app',
    '/Applications/Utilities/Activity Monitor.app',
    '/Applications/Utilities/Console.app',
    '/Applications/Utilities/Disk Utility.app',
    '/Applications/Utilities/Migration Assistant.app',
    '/Applications/Utilities/Terminal.app',
]
dock = Dock()
dock.items['persistent-apps'] = []
for item in tech_dock:
    if os.path.exists(item):
        item = dock.makeDockAppEntry(entry)
        dock.items['persistent-apps'].append(item)
dock.save()
```
