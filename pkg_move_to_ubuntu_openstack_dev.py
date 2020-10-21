#!/bin/bash
#
# Author: Chris MacNaughton
#
# This was used to move packages from lp:~ubuntu-server-dev to lp:~ubuntu-openstack-dev.
#
# for package in aodh ...  watcher-dashboard zaqar; do ./pkg-move-to-ubuntu-openstack-dev $package; done
#

basepath=$(pwd)
branches="master stable/liberty stable/mitaka stable/newton stable/ocata stable/pike stable/queens stable/rocky stable/stein stable/train stable/ussuri"

package="$1"
git clone lp:~ubuntu-server-dev/ubuntu/+source/$package
mkdir /tmp/$package
cd $package
for branch in $branches; do
  git checkout $branch
  if [[ "$?" == "0" ]]; then
    # BEGIN update d/control and d/changelog appropriately
    sed -i "s/ubuntu-server-dev/ubuntu-openstack-dev/g" debian/control
    head -n 1 debian/changelog | grep -q UNRELEASED
    if [[ "$?" == "0" ]]; then
      dch --append "d/control: Update VCS paths for move to lp:~ubuntu-openstack-dev."
    else
      dch --rebuild "d/control: Update VCS paths for move to lp:~ubuntu-openstack-dev."
    fi
    debcommit -a
    # END update d/control and d/changelog appropriately
  fi
done
rm -rf /tmp/$package
git checkout master
git remote add new lp:~ubuntu-openstack-dev/ubuntu/+source/$package
git push --all new; git push --tags new;
git push new 'refs/remotes/origin/upstream:refs/heads/upstream'
git push new 'refs/remotes/origin/pristine-tar:refs/heads/pristine-tar'
cd $basepath
