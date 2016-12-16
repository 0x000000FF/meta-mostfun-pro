DESCRIPTION = "merge ini files"
SECTION = "userland"

FILESEXTRAPATHS_prepend := "${THISDIR}/files/:"

SRC_URI = "file://main.py \
		   file://logger.py"

LICENSE = "CLOSED"

PV = "0.0"
PR = "r0"

S = "${WORKDIR}"

#FILESDIR = "${FILE_DIRNAME}/files/"

FILES_${PN}  += " \
  /mostfun/logger/main.py\
  /mostfun/logger/logger.py\
"

do_install() {
        install -v -d  ${D}/mostfun/logger
        install -m 0755 main.py ${D}/mostfun/logger/
        install -m 0755 logger.py ${D}/mostfun/logger/
}
