#!/bin/bash
#
# Update an Ubuntu package to a new upstream release.
#
# Clones the git package from launchpad.
# Downloads and imports the orig upstream tarball.
# Leaves you in d/changelog to edit.
#
# Example: pkg-new-ubuntu-release cinder 8.0.0~b2 master
#

set -ex

if [ $# -ne 3 ]
then
    echo "Usage: $0 package-name ubuntu-version branch-name"
    echo "       $0 cinder 8.0.0~b1 master"
    echo "       $0 cinder 7.0.1 stable/liberty"
    exit
fi

package=$1
version=$2
branch=$3

git clone lp:~ubuntu-openstack-dev/ubuntu/+source/$package
cd $package

git checkout pristine-tar
git checkout upstream
git checkout $branch

set +e
uscan --verbose --download-version ${version} --rename --timeout 60 # --force-download
set -e
gbp import-orig --no-interactive --merge-mode=replace ../${package}_${version}.orig.tar.gz || \
gbp import-orig --no-interactive --merge-mode=replace ../${package}_${version}.orig.tar.xz

dch -i
sed -i "1s/1ubuntu1/0ubuntu1/" debian/changelog
