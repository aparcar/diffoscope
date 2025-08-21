#!/bin/sh

echo "Generating the debian/tests/control file..."

cat > debian/tests/control.tmp << EOF
# DON'T MANUALLY MODIFY!
# EDIT debian/tests/control.in INSTEAD!
#
EOF

cat debian/tests/control.in >> debian/tests/control.tmp

sed -i "s#%RECOMMENDS%#$(bin/diffoscope --list-debian-substvars | sed -ne 's,^diffoscope:Recommends=,,p')#" debian/tests/control.tmp

sed -i "s#%PYRECOMMENDS%#$(debian/tests/generate-recommends.py)#" debian/tests/control.tmp

# Don't test-depend on radare2; not in bullseye for security reasons. (#950372)
sed -i "s#radare2, ##" debian/tests/control.tmp

sed -i "s,python3-python-debian,python3-debian," debian/tests/control.tmp
sed -i "s,python3-rpm-python,python3-rpm," debian/tests/control.tmp

sed -i "s,\(coreboot-utils\),\1 [!risv64]," debian/tests/control.tmp
sed -i "s,\(fp-utils\),\1 [!riscv64 !s390x]," debian/tests/control.tmp
sed -i "s,\(mono-devel (>= 6.14.1+ds-3)\),\1 [!riscv64]," debian/tests/control.tmp
sed -i "s,\(mono-utils (<< 6.14.1+ds-3)\),\1 [!riscv64]," debian/tests/control.tmp
sed -i "s,\(oggvideotools\),\1 [!s390x]," debian/tests/control.tmp
#sed -i "s,python3-androguard,androguard," debian/tests/control.tmp
#sed -i "s,\(dexdump\),\1 [amd64 arm64 armhf i386]," debian/tests/control.tmp
# aapt removed due to not being in trixie atma - #1070416
# also remove androguard and dexdump for the same reason
#sed -i "s,\(aapt\),\1 [amd64 arm64 armel armhf i386 mips64el mipsel]," debian/tests/control.tmp
sed -i "s#aapt, ##" debian/tests/control.tmp
sed -i "s#dexdump, ##" debian/tests/control.tmp
sed -i "s#python3-androguard, ##" debian/tests/control.tmp
