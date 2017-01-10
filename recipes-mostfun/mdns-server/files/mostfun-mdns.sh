#!/bin/sh
IP=`ifconfig | grep -C 1 wlan0 | grep 'inet addr' | cut -d: -f2 | awk '{ print $1}'`
dns-sd -P mostfunpro _http local 80 `hostname` ${IP} mostfunPro_3Dprinter