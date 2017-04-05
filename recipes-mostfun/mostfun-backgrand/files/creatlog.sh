#!/bin/bash

hostname > /tmp/log.txt
journalctl _SYSTEMD_UNIT=mostfun_panel.service >> /tmp/log.txt
