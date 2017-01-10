SUMMARY = "libclipper"
DESCRIPTION = "libclipper."
HOMEPAGE = ""
SECTION = "console/tools"
LICENSE = "AGPLv3"
LIC_FILES_CHKSUM = "file://../License.txt;md5=8e4ed4217fa0e1ebecd6214c4fd33577"

S="${WORKDIR}/git/cpp/"

PV = "0.1"
PR = "r0"
SRCREV = "${AUTOREV}"
SRC_URI = "git:///media/qqq/workspace/git/clipper;protocol=file"

inherit cmake

BBCLASSEXTEND = "native nativesdk"
