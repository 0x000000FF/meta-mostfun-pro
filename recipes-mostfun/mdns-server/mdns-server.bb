SECTION = "kernel/userland"
LICENSE = "CLOSED"

inherit systemd

FILESEXTRAPATHS_prepend := "${THISDIR}/files/:"

PV = "0.1"
PR = "r0"

SYSTEMD_SERVICE_${PN} = "mostfun-mdns.service"
SYSTEMD_AUTO_ENABLE = "enable"
SRC_URI = " \
    file://mostfun-mdns.service \
    file://mostfun-mdns.sh \
"

S = "${WORKDIR}"

FILESDIR = "${FILE_DIRNAME}/files/"


do_install() {
    install -d ${D}/etc/mdns
    install -m 755 ${WORKDIR}/mostfun-mdns.sh ${D}/etc/mdns/

    if ${@base_contains('DISTRO_FEATURES','systemd','true','false',d)}; then
        install -d ${D}/${systemd_unitdir}/system
        install -m 644 ${WORKDIR}/mostfun-mdns.service ${D}${systemd_unitdir}/system/
        
    fi
}

