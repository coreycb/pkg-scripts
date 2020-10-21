#!/bin/bash
#
# Merges a repo into a debian openstack repo to sponsort someone.
#
# Example: pkg-git-merge-debian python-congressclient debian/newton git://git.launchpad.net/~ddellav/ubuntu/+source/python-congressclient
#

set -ex

if [ $# -ne 3 ]
then
    echo "Usage: $0 package-name release-branch sponsoree-repo"
    echo "       $0 python-congressclient debian/newton git://git.launchpad.net/~ddellav/ubuntu/+source/python-congressclient"
    exit
fi

package=$1
branch=$2
repo=$3

git clone git+ssh://git.debian.org/git/openstack/$package
cd $package

git checkout $branch

#git remote add --tags sponsoree $repo
git remote add sponsoree $repo
git fetch sponsoree

git checkout $branch
git merge --ff-only sponsoree/$branch

cd -
