#!/bin/bash
#
# Update an Ubuntu package to a new upstream snapshot.
#
# Clones git package from upstream into upstream directory.
# Clones git package from launchpad into pkg directory.
# Generates orig tarball from upstream branch and imports to package branch.
# Leaves you in d/changelog to edit.
#
# Note: The following needs to be in ~/.gbp.conf:
#       [import-orig]
#       postimport = dch -v%(version)s New upstream version.
#
# Examples: pkg-snapshot-version cinder master
#           pkg-snapshot-version cinder stable/mitaka
#

set -ex

if [ $# -ne 2 ]
then
    echo "Usage: $0 package-name branch-name"
    echo "       $0 cinder master"
    echo "       $0 cinder stable/mitaka"
    exit
fi

package=$1
branch=$2

rm -rf ~/tarballs
[ -d upstream ] || mkdir upstream
[ -d pkg ] || mkdir pkg
[ -d pkg/${package} ] && rm -rf pkg/${package}

# clone upstream branch and generate snapshot tarball
cd upstream
if [ "$package" = "openstack-trove" ]
then
    git clone https://github.com/openstack/trove || true
    cd trove
else
    git clone https://github.com/openstack/$package || true
    cd $package
fi
git checkout $branch
git pull
pkgos-generate-snapshot
cd ../..

# clone package branch and import snapshot tarball
cd pkg
git clone lp:~ubuntu-openstack-dev/ubuntu/+source/$package || true
cd $package
git pull
git checkout pristine-tar
git checkout upstream
git checkout $branch
if [ "$package" = "openstack-trove" ]
then
    package="trove"
fi
gbp import-orig --no-interactive --merge-mode=replace ~/tarballs/*${package}_*.orig.tar.gz
cp ~/tarballs/*${package}* ..

dch -i
sed -i "1s/1ubuntu1/0ubuntu1/" debian/changelog
