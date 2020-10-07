#!/bin/bash
#
# Update an Ubuntu package to a new upstream snapshot.
# Rename the version with git naming convention based on specified
# version to sort *before*. The date stamp and upstream tip git hash
# will be added to the version.
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
# Examples: pkg-snapshot-version-git cinder 8.0.0~b1 master
#           pkg-snapshot-version-git cinder 8.0.0~b1 stable/mitaka
#

set -ex

if [ $# -ne 3 ]
then
    echo "Usage: $0 package-name version branch-name"
    echo "       $0 cinder 8.0.0~b1 master"
    echo "       $0 cinder 8.0.0~b1 stable/mitaka"
    exit
fi

package=$1
version=$2
branch=$3

rm -rf ~/tarballs
[ -d upstream ] || mkdir upstream
[ -d pkg ] || mkdir pkg
[ -d pkg/${package} ] && rm -rf pkg/${package}

# clone upstream branch and generate snapshot tarball
cd upstream
if [ "$package" = "gnocchi" ]
then
    git clone https://github.com/gnocchixyz/gnocchi.git || true
    cd gnocchi
elif [ "$package" = "networking-arista" ]
then
    git clone https://opendev.org/x/networking-arista || true
    cd networking-arista
elif [ "$package" = "networking-l2gw" ]
then
    git clone https://opendev.org/x/networking-l2gw || true
    cd networking-l2gw
elif [ "$package" = "openstack-trove" ]
then
    git clone https://opendev.org/openstack/trove || true
    cd trove
elif [ "$package" = "zvmcloudconnector" ]
then
    git clone https://github.com/mfcloud/python-zvm-sdk || true
    cd python-zvm-sdk
elif [ "$package" = "neutron-taas" ]
then
    git clone https://opendev.org/x/tap-as-a-service.git || true
    cd tap-as-a-service
else
    git clone https://opendev.org/openstack/$package || true
    cd $package
fi
git checkout $branch
git pull
pkgos-generate-snapshot
githash=$(git rev-parse --short HEAD)
cd ../..

# clone package branch and import snapshot tarball
cd pkg
git clone lp:~ubuntu-openstack-dev/ubuntu/+source/$package || true
cd $package
git pull
git checkout pristine-tar
git checkout upstream
git checkout $branch
date=$(date +%Y%m%d%H)
if [ "$package" = "openstack-trove" ]
then
    package="trove"
fi
#rename snapshot tarball
if [ "$package" = "networking-arista" ]
then
    mv ~/tarballs/networking_arista*.orig.tar.gz ~/tarballs/${package}_${version}~git${date}.${githash}.orig.tar.gz
elif [ "$package" = "neutron-taas" ]
then
    mv ~/tarballs/tap-as-a-service*.orig.tar.gz ~/tarballs/${package}_${version}~git${date}.${githash}.orig.tar.gz
else
    mv ~/tarballs/*${package}_*.orig.tar.gz ~/tarballs/${package}_${version}~git${date}.${githash}.orig.tar.gz
fi
gbp import-orig --no-interactive --merge-mode=replace ~/tarballs/${package}_*.orig.tar.gz
cp ~/tarballs/${package}* ..

dch -i
sed -i "1s/1ubuntu1/0ubuntu1/" debian/changelog
