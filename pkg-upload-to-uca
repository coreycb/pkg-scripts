#!/bin/bash
#
# Upload a package to the ubuntu cloud archive
#
# Example: pkg-upload-to-uca designate 1.0.2 trusty-liberty 0ubuntu1~cloud0 1:1.0.0-0ubuntu1~cloud0
#

set -ex

if [ $# -lt 5 ]
then
    echo "Usage: $0 package-name version ubuntu-release ubuntu-version last-version-full"
    echo "       $0 designate 1.0.2 trusty-liberty 0ubuntu1~cloud0 1:1.0.0-0ubuntu1~cloud0"
    exit
fi

package=$1
version=$2
release=$3
ubuntu_vers=$4
last_version_full=$5

ubuntu_codename="${release%-*}"
openstack_codename="${release#*-}"

orig_tar=${package}_${version}.orig.tar.gz
cp ../build-area/${orig_tar} ..
debuild --no-lintian -S -sa -nc -uc -us -v${last_version_full} --changes-option=-DDistribution=${ubuntu_codename}
changes_file=${package}_${version}-${ubuntu_vers}_source.changes
debsign -k 0DCDF806 ../$changes_file
dput ppa:ubuntu-cloud-archive/${openstack_codename}-staging ../$changes_file
