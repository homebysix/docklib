# `docklib` Change Log

All notable changes to this project will be documented in this file. This project adheres to [Semantic Versioning](http://semver.org/).


## [Unreleased]

Nothing yet.


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


[Unreleased]: https://github.com/homebysix/docklib/compare/v1.0.4...HEAD
[1.0.4]: https://github.com/homebysix/docklib/compare/v1.0.3...v1.0.4
[1.0.3]: https://github.com/homebysix/docklib/compare/v1.0.2...v1.0.3
[1.0.2]: https://github.com/homebysix/docklib/compare/v1.0.1...v1.0.2
[1.0.1]: https://github.com/homebysix/docklib/compare/v1.0.0...v1.0.1
