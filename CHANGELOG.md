# `docklib` Change Log

All notable changes to this project will be documented in this file. This project adheres to [Semantic Versioning](http://semver.org/).

## [2.0.0] - 2024-04-13

This release fixes compatibility with Python 10.12 by removing the dependencies on `distutils.versions`. (Thanks to @arubdesu for #42.)

### Removed

- Removed Python 2 support. If you're still deploying docklib to macOS versions prior to Monterey 12.3, be sure you're deploying a Python runtime like [MacAdmins Python](https://github.com/macadmins/python) rather than relying on the built-in `/usr/bin/python`.
- Removed macOS version detection. This may cause unexpected behavior when referencing the `AllowDockFixupOverride`, `show-recents`, `recent-apps`, `dblclickbehavior`, `show-recents-immutable`, and `windowtabbing` keys on macOS versions prior to Big Sur 11.0.

### Changed

- `makeDockAppSpacer()` parameter name has changed from `type` to `tile_type`. Please update your scripts if you use this function.
- Updated unit tests with new `is-beta` preference key present in macOS Sonoma Dock tiles.

## [1.3.0] - 2021-05-31

The focus of this release is to make docklib functions less focused on dock item labels, since labels can change depending on the user's selected language. (See [#32](https://github.com/homebysix/docklib/issues/32) for details.)

### Added

- A new `findExistingEntry` function that can find dock items based on several attributes.

    The default behavior of `findExistingEntry` is to match the provided string on (in order of preference):

    1. label
    2. path
    3. filename with extension
    4. filename without extension

    The `match_on` parameter can be specified to select only one of those attributes to match, if desired. See the `findExistingEntry` function docstring for available parameters and values.

### Changed

- The `findExistingLabel` function is now simply a pointer to the new `findExistingEntry` function. `findExistingLabel` will be maintained for backward-compatibility.

- The `removeDockEntry` function has a new `match_on` parameter that mirrors the same parameter in `findExistingEntry`. Default behavior is to match on the same attributes listed above, in the same order of preference. (This is a change in behavior from previous versions of docklib. If you prefer to continue removing items solely based on label, you should specify `match_on="label"` in your function call.)

- The `replaceDockEntry` function has two new parameters:
    - `match_str`, which allows specifying the item intended to be replaced in the dock (replaces the now deprecated `label` parameter).
    - `match_on`, which mirrors the same parameter in `findExistingEntry`. Default behavior is to match on the same attributes listed above, in the same order of preference.

### Deprecated

- The `label` parameter of `replaceDockEntry` is deprecated, and it's encouraged to use `match_str` instead. This allows existing items to be replaced based on multiple attributes rather than just label. As stated above, this makes dock customization scripts more reliable in multilingual environments.

    A warning has been added that alerts administrators to this deprecation.

- **This is the last release of docklib that will support Python 2.** Future releases will only be tested in Python 3.

    If you haven't started bundling a Python 3 runtime for your management tools, [this blog article from @scriptingosx](https://scriptingosx.com/2020/02/wrangling-pythons/) is a good read. Also: a reminder that docklib is already included in the "recommended" flavor of the [macadmins/python](https://github.com/macadmins/python) packages.

## [1.2.1] - 2021-03-01

### Added

- Signed GitHub release package

### Fixed

- Fixed issue preventing `findExistingLabel` from finding URLs' labels

## [1.2.0] - 2020-10-15

(Includes changes from briefly-published versions 1.1.0 and 1.1.1.)

### Added

- Published docklib to PyPI so that administrators can manage it with `pip` and more easily bundle it in [custom Python frameworks](https://github.com/macadmins/python). Adjusted repo file structure to match Python packaging standards.
- Created __build_pkg.sh__ script for creation of macOS package installer.
- Added `findExistingURL` and `removeDockURLEntry` functions for handling URL items.
- Created a few basic unit tests.

### Changed

- Updated pre-commit configuration.


## [1.0.5] - 2020-01-29

### Fixed

- Avoids a TypeError that occurred when a dock "section" was None ([#24](https://github.com/homebysix/docklib/issues/24), fixed by [#25](https://github.com/homebysix/docklib/pull/25))

### Changed

- Specified UTF-8 encoding on docklib.py file.


## [1.0.4] - 2019-10-08

### Fixed

- Changed `.append()` to `.extend()` for Python 3 compatibility.


## [1.0.3] - 2019-09-07

### Added

- Added more mutable keys (thanks [@WardsParadox](https://github.com/WardsParadox))
- Added Apache 2.0 license

### Fixed

- Fixed issues with attribute names that contain hyphens (e.g. `mod-count`)
- Fixed issue that caused False values to be skipped


## [1.0.2] - 2019-04-02

### Fixed

- Only use "show-recents" key in 10.14 or higher


## [1.0.1] - 2019-03-24

### Added

- Added the ability to specify a label for Apps
- Added "show-recents" key
- Added pre-commit config for contributors

### Changed

- Standardized Python using Black formatter
- Adopted MunkiPkg project structure

### Fixed

- Corrected examples in read me
- Fixed assignment of return value


## 1.0.0 - 2018-04-19

- Initial release


[Unreleased]: https://github.com/homebysix/docklib/compare/v1.3.0...HEAD
[1.3.0]: https://github.com/homebysix/docklib/compare/v1.2.1...v1.3.0
[1.2.1]: https://github.com/homebysix/docklib/compare/v1.2.0...v1.2.1
[1.2.0]: https://github.com/homebysix/docklib/compare/v1.0.5...v1.2.0
[1.0.5]: https://github.com/homebysix/docklib/compare/v1.0.4...v1.0.5
[1.0.4]: https://github.com/homebysix/docklib/compare/v1.0.3...v1.0.4
[1.0.3]: https://github.com/homebysix/docklib/compare/v1.0.2...v1.0.3
[1.0.2]: https://github.com/homebysix/docklib/compare/v1.0.1...v1.0.2
[1.0.1]: https://github.com/homebysix/docklib/compare/v1.0.0...v1.0.1
