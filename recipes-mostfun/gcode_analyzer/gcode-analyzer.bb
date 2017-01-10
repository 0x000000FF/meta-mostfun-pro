DESCRIPTION = "mostfun gcode analyzer"
SECTION = "userland"

FILESEXTRAPATHS_prepend := "${THISDIR}/files/:"

SRC_URI = "file://gcode_analyzer"

LICENSE = "CLOSED"

PV = "0.0"
PR = "r1"

RDEPENDS_${PN} += "qtbase"

S = "${WORKDIR}"

#FILESDIR = "${FILE_DIRNAME}/files/"

FILES_${PN}  += " \
 /mostfun/gcode_analyzer\
"

do_install() {
        install -v -d  ${D}/mostfun/
        install -m 0755 gcode_analyzer ${D}/mostfun/
}
