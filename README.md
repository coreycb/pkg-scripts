New snapshot version for CI
---------------------------
1. cd ~/pkg/newton
2. pkg-snapshot-version cinder master
3. gpagpt [1]

New upstream (point) release
----------------------------
1. cd ~/pkg/liberty/pkg
2. pkg-new-ubuntu-release neutron 8.3.0 stable/mitaka
3. merge any Ubuntu archive delta
4. update d/control, etc
5. pkg-tag-and-release neutron 8.3.0 xenial 0ubuntu1
6. gpagpt
7. dput ../build-area/neutron_8.3.0-0ubuntu1_source.changes

New upstream point release for direct upload to UCA
---------------------------------------------------
1. cd ~/pkg/liberty/pkg
2. pkg-new-ubuntu-release neutron 7.2.0 stable/liberty
3. merge any UCA delta
4. update d/control, etc
5. pkg-tag-and-release neutron 7.2.0 trusty-liberty 0ubuntu1~cloud0
6. gpagpt
7. pkg-upload-to-uca neutron 7.2.0 trusty-liberty 0ubuntu1~cloud0 2:7.1.2-0ubuntu1~cloud0

Sponsor package for direct upload to UCA
----------------------------------------
1. cd ~/pkg/liberty/pkg
2. pkg-git-merge-ubuntu nova git://git.launchpad.net/~ddellav/ubuntu/+source/nova stable/liberty
3. merge any UCA delta
4. pkg-tag-and-release nova 1.0.1 trusty-liberty 0ubuntu1~cloud0
5. gpagpt
6. pkg-upload-to-uca nova 12.0.5 trusty-liberty 0ubuntu1~cloud0 2:12.0.4-0ubuntu1~cloud2

Generate git repo for launchpad source package
----------------------------------------------
1. cd ~/pkg/ocata/pkg
2. pkg-lp-to-ubuntu-server-dev python-oslo.db

[1] alias gpagpt='git push --all && git push --tags'
