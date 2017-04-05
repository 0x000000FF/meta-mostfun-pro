DESCRIPTION = "for mostfun pro usbhub"
SECTION = "userland"

FILESEXTRAPATHS_prepend := "${THISDIR}/files/:"

RDEPENDS_${PN} += "bash"

SRC_URI = "file://creatlog.sh"

LICENSE = "CLOSED"

PV = "0.0"
PR = "r0"

inherit systemd update-alternatives
S = "${WORKDIR}"

FILESDIR = "${FILE_DIRNAME}/files/"

FILES_${PN}  += " \
 /etc/creatlog.sh\
"

do_install() {
    install -v -d  ${D}/etc/
    install -m 0755 creatlog.sh ${D}/etc/

}
