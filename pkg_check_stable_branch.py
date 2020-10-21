#!/bin/bash
#
# Check if stable branch exists for the specified package.
#
# Example: pkg-check-stable-branch cinder stable/pike
#

# set -ex

if [ $# -ne 2 ]; then
    echo "Usage: $0 package-name stable-branch-name"
    echo "       $0 cinder stable/pike"
    exit
fi

package_name=$1
stable_branch=$2

git clone --quiet lp:~ubuntu-openstack-dev/ubuntu/+source/${package_name} || true
cd ${package_name}

git show-ref --verify --quiet refs/remotes/origin/${stable_branch}
if [ $? -ne 0 ]; then
    echo "NO: ${stable_branch} does not exist for ${package_name}"
    exit 1
else
    echo "YES: ${stable_branch} exists for ${package_name}"
    exit 0
fi
