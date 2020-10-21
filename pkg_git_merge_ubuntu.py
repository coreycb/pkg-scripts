#!/bin/bash
#
# Merges a repo into a core package to sponsor a contribution.
#
# Examples: pkg-git-merge-ubuntu barbican https://git.launchpad.net/~chris.macnaughton/+git/barbican master
#           pkg-git-merge-ubuntu barbican https://git.launchpad.net/~chris.macnaughton/+git/barbican stable/liberty
#

set -ex

if [ $# -ne 3 ]
then
    echo "Usage: $0 package-name sponsoree-repo branch"
    echo "       $0 barbican git://git.launchpad.net/~chris.macnaughton/ubuntu/+source/barbican master"
    echo "       $0 barbican git://git.launchpad.net/~chris.macnaughton/ubuntu/+source/barbican stable/train"
    exit
fi

package=$1
repo=$2
branch=$3

git clone lp:~ubuntu-openstack-dev/ubuntu/+source/$package
cd $package

git checkout pristine-tar
git checkout upstream
git checkout $branch

git remote add sponsoree $repo
git fetch sponsoree

git checkout upstream
git merge --ff-only sponsoree/upstream

git checkout pristine-tar
git merge --ff-only sponsoree/pristine-tar

git checkout $branch
git merge --ff-only sponsoree/$branch
