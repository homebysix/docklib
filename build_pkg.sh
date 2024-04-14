#!/bin/bash

# NOTE: This script is DEPRECATED as of docklib v2.0.0. See release notes here:
# https://github.com/homebysix/docklib/releases/tag/v2.0.0

# Name of pkg signing certificate in keychain. (Default to unsigned.)
CERTNAME="$1"

cd "$(dirname "$0")" || exit 1

echo "Preparing source folder..."
rm -rfv ./docklib/__pycache__
rm -fv ./docklib/*.pyc

echo "Preparing pkgroot and output folders..."
PKGROOT=$(mktemp -d /tmp/docklib-build-root-XXXXXXXXXXX)
OUTPUTDIR=$(mktemp -d /tmp/docklib-output-XXXXXXXXXXX)
mkdir -p "$PKGROOT/Library/ManagedFrameworks/Python/Python3.framework/Versions/Current/lib/python3.10/site-packages/"

echo "Copying docklib into pkgroot..."
# Customize this path to match the Python runtime you're deploying to your managed Macs
cp -R ./docklib "$PKGROOT/Library/ManagedFrameworks/Python/Python3.framework/Versions/Current/lib/python3.10/site-packages/docklib"

echo "Determining version..."
VERSION=$(awk -F \" '/version/{print $2}' docklib/__init__.py)
echo "  Version: $VERSION"

echo "Building package..."
OUTFILE="$OUTPUTDIR/docklib-$VERSION.pkg"
pkgbuild --root "$PKGROOT" --identifier com.elliotjordan.docklib --version "$VERSION" "$OUTFILE"

if [[ -n $CERTNAME ]]; then
    echo "Signing package..."
    productsign --sign "$CERTNAME" "$OUTFILE" "${OUTFILE/.pkg/-signed.pkg}"
    mv "${OUTFILE/.pkg/-signed.pkg}" "$OUTFILE"
fi

echo "$OUTFILE"
open "$OUTPUTDIR"
