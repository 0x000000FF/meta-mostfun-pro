DESCRIPTION = "check opkg update"
SECTION = "userland"
LICENSE = "CLOSED"

FILESEXTRAPATHS_prepend := "${THISDIR}/files/:"


SRC_URI = "file://checkupdate.sh \
           file://checkupdate.service \
           file://doupgrade.sh \
           file://doupgrade.service"


PV = "0.1"
PR = "r1"

SYSTEMD_SERVICE_${PN} = "checkupdate.service"
SYSTEMD_AUTO_ENABLE = "disable"
SYSTEMD_SERVICE_${PN} += "doupgrade.service"
SYSTEMD_AUTO_ENABLE = "disable"

S = "${WORKDIR}"

inherit systemd update-alternatives

FILESDIR = "${FILE_DIRNAME}/files/"

FILES_${PN}  += " \
 /etc/checkupdate.sh \
 /etc/doupgrade.sh \
"

do_install() {
	install -v -d  ${D}/etc/
    install -m 0755 checkupdate.sh ${D}/etc/
    install -m 0755 doupgrade.sh ${D}/etc/

    if ${@base_contains('DISTRO_FEATURES','systemd','true','false',d)}; then
        install -d ${D}/${systemd_unitdir}/system
        install -m 644 ${WORKDIR}/checkupdate.service ${D}${systemd_unitdir}/system/
        install -m 644 ${WORKDIR}/doupgrade.service ${D}${systemd_unitdir}/system/
	fi
}

