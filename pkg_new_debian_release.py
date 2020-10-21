#!/bin/bash
#
# Update an Ubuntu package to a new upstream release.
#
# Clones the git package from alioth.
# Downloads and imports the new release's orig upstream tarball.
# Leaves you in d/changelog to edit.
# Also leaves you in d/gbp.conf if a new branch was created.
#
# Example: pkg-new-debian-release python-cinderclient 1.5.0 debian/newton
#

set -ex

if [ $# -ne 3 ]
then
    echo "Usage: $0 package-name version branch"
    echo "       $0 python-cinderclient 1.5.0 debian/newton"
    echo "       $0 python-cinderclient 1.5.0 ubuntu/mitaka"
    exit
fi

package=$1
version=$2
branch=$3

git clone git+ssh://git.debian.org/git/openstack/$package
#gbp clone git+ssh://git.debian.org/git/python-modules/packages/$package
cd $package

set +e
git branch -a | grep $branch
if [ $? -eq 0 ]
then
    set -e
    git checkout $branch
    update_gbp_conf=false
else
    set -e
    git checkout -b $branch
    update_gbp_conf=true
fi

./debian/rules fetch-upstream-remote
git merge -X theirs $version

dch -i

./debian/rules gen-orig-xz

if [ "$update_gbp_conf" == true ]
then
   vim debian/gbp.conf
fi

vim .gitreview
echo "Make sure .gitreview matches what is in generated orig tarball"
