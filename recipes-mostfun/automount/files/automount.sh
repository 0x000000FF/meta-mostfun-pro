#!/bin/bash
USBPORT=`echo -e ${1} | cut -d / -f 8 | cut -d . -f 2`
DEVICE=${2}
if [ ${USBPORT} -eq 4 ]; 
	then
	mkdir /media/sdcard
	mount -o iocharset=utf8 /dev/${DEVICE} /media/sdcard
#/etc/autoinstall.sh /media/sdcard
fi

if [ ${USBPORT} -eq 3 ]; 
	then
	mkdir /media/usb
	mount -o iocharset=utf8 /dev/${DEVICE} /media/usb
#/etc/autoinstall.sh /media/usb
fi