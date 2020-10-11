#!/bin/bash

cd "$(dirname "$0")" || exit 1

echo "Preparing source folder..."
rm -rfv ./docklib/__pycache__
rm -fv ./docklib/*.pyc

echo "Preparing pkgroot and output folders..."
PKGROOT=$(mktemp -d /tmp/docklib-build-root-XXXXXXXXXXX)
OUTPUTDIR=$(mktemp -d /tmp/docklib-output-XXXXXXXXXXX)
mkdir -p "$PKGROOT/Library/Python/2.7/site-packages/"

echo "Copying docklib into pkgroot..."
# Customize this path if you're not using the macOS built-in Python 2.7 with docklib.
cp -R ./docklib "$PKGROOT/Library/Python/2.7/site-packages/docklib"

echo "Determining version..."
VERSION=$(awk -F \" '/version/{print $2}' docklib/__init__.py)
echo "  Version: $VERSION"

echo "Building package..."
OUTFILE="$OUTPUTDIR/docklib-$VERSION.pkg"
pkgbuild --root "$PKGROOT" --identifier com.elliotjordan.docklib --version "$VERSION" "$OUTFILE"
echo "$OUTFILE"
open "$OUTPUTDIR"
