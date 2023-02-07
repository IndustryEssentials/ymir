#!/bin/sh

set -e

# get version
YMIR_VERSION=`grep -Po "(?<=YMIR_VERSION = ')(\d+\.\d+\.\d+)" ../ymir/command/mir/version.py`

mkdir deb-workplace/DEBIAN/ -p
mkdir deb-workplace/usr/ymir -p
cp ../ymir.sh ../.env ../docker-compose.dev.yml ../docker-compose.labelfree.yml \
   ../docker-compose.label_studio.yml ../docker-compose.modeldeploy.yml ../docker-compose.yml \
   deb-workplace/usr/ymir

cat <<EOT > deb-workplace/DEBIAN/control
Package: YMIR
Version: ${YMIR_VERSION}
Priority: optional
Depends:
Suggests:
Architecture: amd64
Maintainer: ymir
Provides: ymir
Description: YMIR
EOT

cat <<EOT > deb-workplace/DEBIAN/postinst
#!/bin/sh
echo "Successfully installed ymir, please go to installation dir (default: /usr/ymir) and run ./ymir.sh start"
EOT

chmod +x deb-workplace/DEBIAN/postinst

dpkg-deb -b deb-workplace ymir-linux-amd64-${YMIR_VERSION}.deb

rm -rf deb-workplace
