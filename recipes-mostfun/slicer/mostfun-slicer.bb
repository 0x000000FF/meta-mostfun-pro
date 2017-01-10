DESCRIPTION = "model slicer"

FILESEXTRAPATHS_prepend := "${THISDIR}/files/:"

SRC_URI = "file://CuraEngine \
			file://default.cfg"

LICENSE = "CLOSED"

PV = "0.0"
PR = "r0"

S = "${WORKDIR}"


FILES_${PN}  += " \
 /mostfun/slicer/CuraEngine \
 /mostfun/slicer/default.cfg \
"
FILESDIR = "${FILE_DIRNAME}/files/"

inherit update-alternatives

do_install() {
        install -v -d  ${D}/mostfun/slicer/
        cp CuraEngine ${D}/mostfun/slicer/
        cp default.cfg ${D}/mostfun/slicer/
}
