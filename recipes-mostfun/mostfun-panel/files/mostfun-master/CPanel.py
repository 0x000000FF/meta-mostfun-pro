#!/usr/bin/env python
# coding: utf-8
from app import create_app
from os import getenv

__author__ = 'Jux.Liu'

app = create_app(getenv('FLASK_CONFIG') or 'default')

if __name__ == '__main__':
    from app.modules.device import UI

    UI.UI_monitor()
    # 编辑以下路径文件最后一行来修改默认启动界面的端口，解决端口冲突问题/usr/lib/edison_config_tools/edison-config-server.js
    app.run(host='0.0.0.0', port=80, debug=False, threaded=True)
