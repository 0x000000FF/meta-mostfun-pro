DESCRIPTION = "online update config file,the URLs"
SECTION = "userland"

FILESEXTRAPATHS_prepend := "${THISDIR}/files/:"


SRC_URI = "file://cnfeeds \
			file://eufeeds \
			file://hkfeeds \
			file://usfeeds.conf \
			"

LICENSE = "CLOSED"

PV = "0.4"
PR = "r5"

S = "${WORKDIR}"

inherit allarch update-alternatives

#FILESDIR = "${FILE_DIRNAME}/files/"

FILES_${PN}  += " \
 /etc/opkg/usfeeds.conf \
 /etc/opkg/cnfeeds  \
 /etc/opkg/hkfeeds  \
 /etc/opkg/eufeeds  \
"

do_install() {
	install -v -d  ${D}/etc/opkg/
    install -m 0755 usfeeds.conf ${D}/etc/opkg/
    install -m 0755 eufeeds ${D}/etc/opkg/
    install -m 0755 cnfeeds ${D}/etc/opkg/
    install -m 0755 hkfeeds ${D}/etc/opkg/

}
