DESCRIPTION = "mostfun pro panel"
SECTION = "userland"

FILESEXTRAPATHS_prepend := "${THISDIR}/files/:"

RDEPENDS_${PN} = "python"
RDEPENDS_${PN} += "python-evdev"
RDEPENDS_${PN} += "mraa"
RDEPENDS_${PN} += "bash"
RDEPENDS_${PN} += "buzzer"
RDEPENDS_${PN} += "tft-8340"
RDEPENDS_${PN} += "automount"
RDEPENDS_${PN} += "decode"
RDEPENDS_${PN} += "marlin"
RDEPENDS_${PN} += "mergeini"
RDEPENDS_${PN} += "gcode-analyzer"
RDEPENDS_${PN} += "mdns-server"
RDEPENDS_${PN} += "clipper"
RDEPENDS_${PN} += "logger"
RDEPENDS_${PN} += "mergeini"

SRC_URI = "file://mostfun.des3 \
           file://panel_install.sh \
           file://panel_install.service \
           file://mostfun_panel.service"

LICENSE = "CLOSED"

PV = "1.57.6"
PR = "r25c27a5"

SYSTEMD_SERVICE_${PN} = "panel_install.service"
SYSTEMD_AUTO_ENABLE = "enable"
SYSTEMD_SERVICE_${PN} += "mostfun_panel.service"
SYSTEMD_AUTO_ENABLE = "enable"

inherit systemd update-alternatives

S = "${WORKDIR}"

FILESDIR = "${FILE_DIRNAME}/files/"

FILES_${PN} = "/etc/panel_install.sh \
        /mostfun/mostfun.des3 \
        "

do_install() {
    install -v -d  ${D}/mostfun/
    install -v -d  ${D}/etc/
    install -m 0755 panel_install.sh ${D}/etc/
    install -m 0755 mostfun.des3 ${D}/mostfun/

    if ${@base_contains('DISTRO_FEATURES','systemd','true','false',d)}; then
        install -d ${D}/${systemd_unitdir}/system
        install -m 644 ${WORKDIR}/panel_install.service ${D}${systemd_unitdir}/system/
        install -m 644 ${WORKDIR}/mostfun_panel.service ${D}${systemd_unitdir}/system/
    fi
}
