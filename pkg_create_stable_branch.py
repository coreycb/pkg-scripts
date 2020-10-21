#!/bin/bash
#
# Create a stable branch for the specified package.
#
# Example: pkg-create-stable-branch cinder stable/pike
#

set -ex

if [ $# -ne 2 ]; then
    echo "Usage: $0 package-name stable-branch-name"
    echo "       $0 cinder stable/pike"
    exit
fi

package_name=$1
stable_branch=$2

git clone lp:~ubuntu-openstack-dev/ubuntu/+source/${package_name} || true
cd ${package_name}

git branch | grep master
if [ $? -ne 0 ]; then
    echo "ERROR: not on master branch"
    exit 1
fi

set +e
git branch -a | grep ${stable_branch}
if [ $? -eq 0 ]; then
    echo "ERROR: ${stable_branch} branch already exists"
    exit 1
fi
set -e

git checkout -b ${stable_branch}
sed -i "s|master|${stable_branch}|" "debian/gbp.conf"

dch -n "d/gbp.conf: Create ${stable_branch} branch."
sed -i "/  \* Non-maintainer upload./d" "debian/changelog"

debcommit -a
