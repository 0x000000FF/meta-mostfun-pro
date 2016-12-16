DESCRIPTION = "merge ini files"
SECTION = "userland"

FILESEXTRAPATHS_prepend := "${THISDIR}/files/:"

SRC_URI = "file://main.py"

LICENSE = "CLOSED"

PV = "0.0"
PR = "r0"

S = "${WORKDIR}"

#FILESDIR = "${FILE_DIRNAME}/files/"

FILES_${PN}  += " \
 /mostfun/mergeini/main.py\
"

do_install() {
        install -v -d  ${D}/mostfun/mergeini
        install -m 0755 main.py ${D}/mostfun/mergeini/
}
