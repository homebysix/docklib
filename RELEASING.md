# Releasing new versions of docklib

## Requirements

- Local clone of this repository
- Twine (`pip3 install twine`)
- Account on test.pypi.org
- Account on pypi.org

## Steps

1. Ensure the version in __docklib/\_\_init\_\_.py__ has been updated.

1. Ensure the change log has been updated and reflects actual release date.

1. Merge development branch to main/master branch.

1. Run docklib unit tests and fix any errors:

        managed_python3 -m unittest -v tests.unit

1. Build a new distribution package:

        rm -fv dist/*
        python3 setup.py sdist bdist_wheel

1. Upload package to test.pypi.org:

        twine upload --repository-url https://test.pypi.org/legacy/ dist/*

1. View resulting project on test.pypi.org and make sure it looks good.

1. Install test docklib in MacAdmins Python on a test Mac:

        managed_python3 -m pip install --upgrade -i https://test.pypi.org/simple/ docklib

1. Perform tests - manual for now.

1. Upload package to pypi.org:

        twine upload dist/*

1. View resulting project on pypi.org and make sure it looks good.

1. Install production docklib in MacAdmins Python on a test Mac:

        managed_python3 -m pip install --upgrade docklib

1. Build new installer package using __build_pkg.sh__:

        ./build_pkg.sh

    By default the resulting package is unsigned. To sign the package, provide the name of the signing certificate from your macOS keychain.

        ./build_pkg.sh "Developer ID Installer: John Doe (ABCDE12345)"

1. Create new [release](https://github.com/homebysix/docklib/releases) on GitHub. Add notes from change log. Attach built installer package.

1. Announce to [dock-management](https://macadmins.slack.com/archives/C17NRH534) and other relevant channels, if desired.
