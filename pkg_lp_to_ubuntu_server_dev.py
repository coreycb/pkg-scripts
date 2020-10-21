#!/bin/bash
#
# Pulls package from Launchpad, creates git repo with master, pristine-tar,
# and upstream branches, and pushes it to:
# lp:~ubuntu-openstack-dev/ubuntu/+source/package-name.
#
# Example: pkg-lp-to-ubuntu-openstack-dev python-oslo.db disco
#
set -ex

if [ $# -ne 2 ]
then
    echo "Usage: $0 package-name ubuntu-release"
    echo "       $0 python-oslo.db disco"
    exit
fi

pkg=$1
ubuntu_release=$2
orig_dir=$(pwd)

rm -rf ${pkg}*
pull-lp-source ${pkg} ${ubuntu_release}
mv ${pkg}-* ${pkg}
cd ${pkg}

quilt pop -a || true

rm -rf ${orig_dir}/${pkg}/.pc
rm -rf ${orig_dir}/${pkg}/.git*

git init
git add *
git add */.*
git commit -a -m "Initial import from Launchpad"

git checkout --orphan upstream
git rm --cached -r .
find ${orig_dir}/${pkg}/ -maxdepth 1 ! -name '.git' ! -name "${pkg}" -exec rm -rf {} +
git commit --allow-empty -a -m "Initial branch creation"

git checkout --orphan pristine-tar
git commit --allow-empty -a -m "Initial branch creation"

git checkout --force master
cat > debian/gbp.conf << EOF
[DEFAULT]
debian-branch = master
upstream-tag = %(version)s
pristine-tar = True

[buildpackage]
export-dir = ../build-area
EOF
git add debian/gbp.conf
dch -i "d/gbp.conf: Update gbp configuration file."

debcommit -a
sed -i "s/Vcs-Browser: .*/Vcs-Browser: https:\/\/git\.launchpad\.net\/~ubuntu-openstack-dev\/ubuntu\/+source\/${pkg}/g" debian/control
sed -i "s/Vcs-Git: .*/Vcs-Git: https:\/\/git\.launchpad\.net\/~ubuntu-openstack-dev\/ubuntu\/+source\/${pkg}/g" debian/control
update-maintainer
dch "d/control: Update Vcs-* links and maintainers."
debcommit -a

git push --all lp:~ubuntu-openstack-dev/ubuntu/+source/${pkg}
git push --tags lp:~ubuntu-openstack-dev/ubuntu/+source/${pkg}

echo "Pushed to: https://code.launchpad.net/~ubuntu-openstack-dev/ubuntu/+source/${pkg}/+git/${pkg}"
