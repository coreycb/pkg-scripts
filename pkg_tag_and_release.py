#!/bin/bash
#
# Release an Ubuntu package (but don't upload).
#
# Update release in d/changelog, commit it, tag release, and build/sign src/changes files.
#
# Examples: pkg-tag-and-release zesty
#           pkg-tag-and-release trusty-liberty
#

set -ex

if [ $# -lt 1 ]
then
    echo "Usage: $0 ubuntu-release"
    echo "       $0 zesty"
    echo "       $0 wily"
    exit
fi

package=$(dpkg-parsechangelog --show-field Source)
version=$(dpkg-parsechangelog --show-field Version)
orig_version=$version
release=$1

set +e
rm *.deb *.build *.changes; rm -rf .pc
set -e

sed -i "0,/UNRELEASED/ s/UNRELEASED/$release/" debian/changelog
git commit -m "releasing package $package version $version" debian/changelog

mod_version=$version
[[ "$mod_version" == *:* ]] && mod_version=$(echo $mod_version | sed -n 's/:/%/p')
[[ "$mod_version" == *~* ]] && mod_version=$(echo $mod_version | sed -n 's/~/_/gp')
git tag -s debian/$mod_version -m "tagging package $package version debian/$version"
git tag --list | grep debian/$mod_version

mod_version=$version
[[ "$version" == *:* ]] && mod_version=$(echo $version | sed -n 's/^.*://p')
if [ "$package" == "horizon" ] || [ "$package" == "heat-dashboard" ]; then
    debuild -S -sa -us -uc
    debsign -k 3516D1A5BF0077E71414E19715B9B3EE0DCDF806 ../${package}_${mod_version}_source.changes
else
    gbp buildpackage -S -sa -us -uc
    debsign -k 3516D1A5BF0077E71414E19715B9B3EE0DCDF806 ../build-area/${package}_${mod_version}_source.changes
fi
