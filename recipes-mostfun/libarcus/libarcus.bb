SUMMARY = "libArcus"
DESCRIPTION = "libArcus."
HOMEPAGE = "https://github.com/Ultimaker/libArcus.git"
SECTION = "console/tools"
LICENSE = "AGPLv3"
LIC_FILES_CHKSUM = "file://LICENSE;md5=3d3c0b87ef66889fc868a1fcedef719c"

S="${WORKDIR}/git/"

DEPENDS = "protobuf python"

PV = "0.1"
PR = "r0"
SRCREV = "${AUTOREV}"
SRC_URI = "git://github.com/Ultimaker/libArcus.git;protocol=https;branch=15.10"

SRC_URI[md5sum] = "dc84e9912ea768baa1976cb7bbcea7b5"
SRC_URI[sha256sum] = "eac6969b617f397247e805267da2b0db3ff9e5a9163b123503a192fbb5776567"

#EXTRA_OECONF += " --with-protoc=echo"

inherit cmake autotools

BBCLASSEXTEND = "native nativesdk"
