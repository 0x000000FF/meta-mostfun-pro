#!/usr/bin/env python
# coding: utf-8
'''

'''
# import logging
import os
import shutil
import subprocess
from inspect import getframeinfo, stack
from os import listdir
from os.path import isfile, join, isdir, exists, getsize

from flask import Flask
from flask.ext.login import LoginManager

from config import config

__author__ = 'Jux.Liu'

# log = logging.getLogger('werkzeug')
# log.setLevel(logging.ERROR)
login_manager = LoginManager()


class GlobalParam(object):
    def __init__(self):
        self.LoginList = dict()
        self.mostfun = None
        self.RootPath = r'/mostfun/'
        self.HomePath = r'/home/'
        self.LocalPath = r'/mostfun/panel/'
        self.docPath = r'/mostfun/panel/app/pro-guide/'

        self.SDCard = r'/media/sdcard/'
        self.USB = r'/media/usb/'
        self.Flash = r'/home/mostfuncp/'
        self.PausedPath = r'/paused/'
        self.folder = [self.Flash, self.SDCard, self.USB, self.Flash]

        self.GcodePath = r'/gcode/'
        self.ModelPath = r'/model/'
        self.ModelImgPath = r'/img/'
        self.ModelZipPath = r'/zip/'

        self.TmpFolder = r'/tmp/'
        self.PrtPic = r'/tmp/'
        self.decode = r'/mostfun/decode.mostfun'

        self.log = r'/home/logs/'
        self.cfgbak = r'/home/backup/'
        self.update_list = {}

        self.update_process = 0
        self.total_process = 0
        self.finish_download = False
        self.update_packages_num = 0
        self.download_process = '0%'
        self.package_list = {'data': None}


g_p_ = GlobalParam()


def GetFileList(dir, fileList):
    if isfile(dir):
        fileList.append(dir.decode('gbk'))
    elif isdir(dir):
        for s in listdir(dir):
            # 如果需要忽略某些文件夹，使用以下代码
            # if s == "xxx":
            # continue
            newDir = join(dir, s)
            GetFileList(newDir, fileList)
    return fileList


class Logger(object):
    def __init__(self):
        self.exe = r'python /mostfun/logger/logger.py -{param} -c={caller} -f="{call_file}" -l={lineno} -m="{msg}"'

    def info(self, msg):
        _ = getframeinfo(stack()[1][0])
        cmd = self.exe.format(caller=_.function, call_file=_.filename, lineno=_.lineno, msg=msg, param='i')
        subprocess.call(cmd, shell=True)

    def debug(self, msg):
        _ = getframeinfo(stack()[1][0])
        cmd = self.exe.format(caller=_.function, call_file=_.filename, lineno=_.lineno, msg=msg, param='d')
        subprocess.call(cmd, shell=True)

    def warning(self, msg):
        _ = getframeinfo(stack()[1][0])
        cmd = self.exe.format(caller=_.function, call_file=_.filename, lineno=_.lineno, msg=msg, param='w')
        subprocess.call(cmd, shell=True)

    def error(self, msg):
        _ = getframeinfo(stack()[1][0])
        cmd = self.exe.format(caller=_.function, call_file=_.filename, lineno=_.lineno, msg=msg, param='e')
        subprocess.call(cmd, shell=True)


logger = Logger()
logger.info('start up')

bkcfg = '{0}{1}'.format(g_p_.cfgbak, 'config.ini')
lccfg = '{0}{1}'.format(g_p_.LocalPath, 'config.ini')

if not exists(bkcfg):
    shutil.copyfile(lccfg, bkcfg)

if not exists(lccfg) or getsize(lccfg) < 10:
    shutil.copyfile(bkcfg, lccfg)


if os.path.exists('/etc/opkg/my'):
    with open('/etc/opkg/my', 'r') as m:
        my = m.readline()
else:
    my = ''

CDN_list = {'my': my,
            'cn': 'http://update.mostfun.cc',
            'hk': 'http://update.mostfun.cc',
            'eu': 'http://update.mostfun.cc',
            'us': 'http://update.mostfun.cc'}

def create_app(config_name):
    logger.info('create app')
    app = Flask(__name__)

    cmd = 'python {0}{1}/{2} -s {3} -t {4} {5}'.format(g_p_.RootPath,
                                                       'merge-ini',
                                                       'main.py',
                                                       g_p_.cfgbak + 'config.ini',
                                                       g_p_.LocalPath + 'config.ini',
                                                       '-u')
    subprocess.call(cmd, shell=True)

    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    login_manager.init_app(app)

    from .modules.utils import utils as utils_blueprint

    app.register_blueprint(utils_blueprint)

    from .modules.device import device as device_blueprint

    app.register_blueprint(device_blueprint)

    from .modules.user import user as user_blueprint

    app.register_blueprint(user_blueprint)

    from .modules.filemgr import filemgr as filemgr_blueprint

    app.register_blueprint(filemgr_blueprint)

    from .modules.settings import settings as settings_blueprint

    app.register_blueprint(settings_blueprint)

    from .main import main as main_blueprint

    app.register_blueprint(main_blueprint)

    @app.after_request
    def ar(response):
        response.cache_control.max_age = 0
        return response

    return app
