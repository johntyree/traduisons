#!/bin/bash

#set -x
set -e -o nounset
#trap "read x" DEBUG

CWD=$(pwd)
BUILD="$CWD/build/bdist.linux-x86_64/deb"
TMPPKG="$BUILD/pkg"
DIST="$CWD/dist"
PKGNAM=$(setup.py --name)
#ARCH=$(setup.py --platforms)
ARCH=i386
VERSION=$(setup.py --version)
RELEASE=${RELEASE:-1}
#DESC=$(setup.py --long-description)
DESC="TODO"
#DEPENDS=$(setup.py --requires | sed -e :a -e '$!N;s/\n/, /;ta')
DEPENDS="python (>= 2.5)"
CONTACT=$(setup.py --contact)
CONTACT_EMAIL=$(setup.py --contact-email)

for dir in "$BUILD" "$DIST"; do
    if [[ -d "$dir" ]]; then
        rm -rfv "$dir"
    fi
    mkdir -p "$dir"
done

rm -rf "$TMPPKG"
setup.py install \
    --root "$TMPPKG" \
    --install-lib /usr/share/pyshared
mv "$TMPPKG/usr/doc" "$TMPPKG/usr/share/doc"

PKGSIZE=$(du -s "$TMPPKG" | awk '{ print $1 }')

tar cvzf "$BUILD/data.tar.gz" -C "$TMPPKG" .

cat > "$BUILD/control" <<EOT
Package: $PKGNAM
Version: $VERSION
Section: desktop
Priority: optional
Architecture: $ARCH
Depends: $DEPENDS
Installed-Size: $PKGSIZE
Maintainer: $CONTACT <$CONTACT_EMAIL>
Description: $DESC
EOT
tar cvzf "$BUILD/control.tar.gz" -C "$BUILD" "control"

echo '2.0' > "$BUILD/debian-binary"

ar rcv "$BUILD/package.deb" \
    "$BUILD/debian-binary" \
    "$BUILD/control.tar.gz" \
    "$BUILD/data.tar.gz"

mv -v "$BUILD/package.deb" "$DIST/$PKGNAM-$VERSION-$RELEASE-$ARCH.deb"
