#!/bin/sh
mkdir -p debian/usr/lib/python2.5/site-packages/flow
cd ../src && find . -name '*.py' | cpio -pvmud ../packaging/debian/usr/lib/python2.5/site-packages/flow
cd -
mkdir -p debian/usr/lib/python2.5/site-packages/flow/obo
cp ../src/obo/cell.obo debian/usr/lib/python2.5/site-packages/flow/obo
mkdir -p debian/usr/bin/
echo '#!/bin/sh' > debian/usr/bin/flow
echo 'cd /usr/lib/python2.5/site-packages/flow && /usr/bin/python2.5  /usr/lib/python2.5/site-packages/flow/App.py' >> debian/usr/bin/flow
chmod +x debian/usr/bin/flow
echo 'copy bayes.so to debian/usr/lib/python2.5/site-packages/flow/plugins/statistics/Bayes/'
echo 'copy flow.so to debian/usr/lib/python2.5/site-packages/flow/plugins/statistics/Kde/'
echo 'Also do not forget to update the debian/DEBIAN/control'
echo 'then run dpkg-deb --build debian'

