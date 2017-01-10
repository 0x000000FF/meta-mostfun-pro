# -*- coding:utf-8 -*-
"""
    Check System, Panel and 2560 updates.
"""
import shutil
import subprocess
from os import remove
from os.path import exists
from time import sleep

from app import g_p_, logger
from app.modules.filemgr import FileManage
from app.modules.utils.Utils import getINI
from config import Config

__author__ = 'Jux.Liu'

file_manager = FileManage()
config = Config()


def check_sys_update():
    """
检查系统是否有新版本
    :return: 有新版本返回最新版本号，没有则返回“No Update”
    """
    # start check sys update

    url = config.SYS_UPDATE_URL
    version_file = config.VERSION_FILE
    path = g_p_.HomePath
    result = []

    # check update for system
    logger.info('start get system version file')
    res = get_version_file(url, version_file, path)

    if res:
        sys_version = getINI('update', 'version', '{0}{1}'.format(g_p_.HomePath, config.VERSION_FILE))
        logger.info('start check system version file, current version: {0}'.format(sys_version))
        result = check_sys_version(sys_version)

    else:
        logger.warning('get system file failed')
        errcode = 23
        result.append(config.ERR_CODE[errcode])

    return result


def get_version_file(url, version_file, path):
    """
获取version.ini文件
    :param url:
    :param version_file:
    :param path:
    :return:
    """
    if exists(g_p_.SDCard + 'version.ini'):
        logger.info('get version file from SD card')
        shutil.copy(g_p_.SDCard + 'version.ini', g_p_.HomePath)
        res = True
    elif exists(g_p_.USB + 'version.ini'):
        logger.info('get version file from USB device')
        shutil.copy(g_p_.USB + 'version.ini', g_p_.HomePath)
        res = True
    else:
        logger.info('get version file from internet')
        res = file_manager.downloadFile(url=url + version_file, path=path, log=r'/tmp/systemstatus.log')
    logger.info('get version file result: {0}')
    with open(r'/tmp/systemstatus.log', 'w') as f:
        f.write('0')
    return res


def check_sys_version(sys_version):
    """
判断系统是否为最新版本，true则检查opkg是否为最新版本，false则返回系统最新版本号
    :param sys_version: 系统当前的最新版本
    :return: true则返回opkg的最新版本信息，false则返回系统最新版本号
    """
    result = []
    if sys_version.strip() == config.SYS_VERSION.strip():
        logger.info('no system update')
        g_p_.update_list['system_update'] = False
        details = check_opkg_upgrade()
        result = details
    else:
        logger.info('get new system update')
        msgcode = 20
        g_p_.update_list['system_update'] = True
        g_p_.update_list['opkg_update'] = False
        result.append(config.MSG_CODE[msgcode].format(sys_version))
    return result


def check_opkg_upgrade():
    """
检查OPKG是否有新版本更新
    :return: 有新版本返回最新版本号，没有则返回“No Update”
    """
    fn = r'/tmp/upgradelist.txt'
    if exists(fn):
        pass
    else:
        logger.info('start check opkg update')
        subprocess.call('systemctl start checkupdate', shell=True)

    details = get_opkg_update_details(fn)

    if len(details) == 0:
        remove(fn)
        logger.info('')
        g_p_.update_list['opkg_update'] = False
        details.append('No Update')

    else:
        g_p_.update_list['opkg_update'] = True
        g_p_.update_packages_num = len(details)

    return details


def get_opkg_update_details(fn):
    """
获取opkg更新的版本详情
    :param fn: 版本信息文件
    :return: 更新opkg的版本信息
    """
    flag = True
    logger.info('check opkg update start')
    subprocess.Popen('systemctl start checkupdate', shell=True)
    while flag:
        sleep(1)
        p = subprocess.Popen('systemctl status checkupdate | grep Active', shell=True, stdout=subprocess.PIPE)
        p.wait()
        out = p.stdout.readlines()[0].strip().split(':')
        if 'inactive' in out[1]:
            flag = False
    logger.info('check opkg update done')
    with open(fn) as f:
        details = f.readlines()
    return details


def copy_new_system_file():
    file_name = 'toFlash.tar.gz'
    file_name_sd = g_p_.SDCard + file_name
    file_name_usb = g_p_.USB + file_name
    try:
        if exists(file_name_sd):
            logger.info('copy file system from SD card')
            shutil.copy(file_name_sd, g_p_.HomePath)
        elif exists(file_name_usb):
            logger.info('copy file system from USB device')
            shutil.copy(file_name_usb, g_p_.HomePath)
        else:
            return False
    except Exception as e:
        return False
    else:
        return True


def start_update():
    """
开始更新操作
    :return:
    """
    if g_p_.mostfun.state not in ['ready', 'error']:

        # stop update, wait for print finish
        errcode = 26
        logger.warninging('update failed: {0}'.format(config.ERR_CODE[errcode]))
        return {'result': False,
                'msg'   : config.ERR_CODE[errcode]}

    else:
        if g_p_.update_list['system_update']:
            res = update_sys()
            return res

        if g_p_.update_list['opkg_update']:
            res = start_opkg_update()
            return res


def start_opkg_update():
    g_p_.mostfun.close_serial()
    subprocess.call('systemctl start blink-led', shell=True)
    g_p_.mostfun.state = 'updating'
    sleep(1)
    res = do_opkg_update()
    subprocess.call('systemctl stop blink-led', shell=True)
    return res


def do_opkg_update():
    logger.info('do opkg update start')
    subprocess.Popen('systemctl start doupgrade', shell=True)
    flag = True
    while flag:
        sleep(1)
        p = subprocess.Popen('systemctl status doupgrade | grep Active', shell=True, stdout=subprocess.PIPE)
        p.wait()
        out = p.stdout.readlines()[0].strip().split(':')
        if 'inactive' in out[1]:
            flag = False
    g_p_.mostfun.open_serial()
    g_p_.mostfun.state = 'ready'
    with open(r'/tmp/upgrade.txt') as f:
        if 'Configuring' in f.readlines()[-1]:
            res = True
        else:
            res = False
    return res


def update_sys():
    """
进行系统更新
    :return:
    """
    # backup files
    logger.info('start updating system')
    for item in config.BAK_LIST:
        shutil.copy(item, config.BAK_PATH)
    # update sys
    url = config.SYS_UPDATE_URL
    file = config.SYS_FILE
    print('{0}{1}'.format(url, file))
    subprocess.call('systemctl start blink-led', shell=True)
    g_p_.mostfun.state = 'updating'

    # start download
    get_new_system_file(url)

    # start check md5
    md5 = getINI('update', 'md5', '{0}{1}'.format(g_p_.HomePath, config.VERSION_FILE))
    logger.info('the package md5 is: {0}'.format(md5))
    print(md5)

    if file_manager.check_md5('{0}{1}'.format(g_p_.HomePath, 'toFlash.tar.gz'), md5):
        return recovery()

    else:
        logger.warning('update system failed: Download file error, md5 not matched')
        subprocess.call('systemctl stop blink-led', shell=True)
        return False


def get_new_system_file(url):
    """
获取最新的系统更新包
    :param url:
    :return:
    """
    file_name = 'toFlash.tar.gz'
    logger.info('download systam package')
    res = file_manager.downloadFile(url='{0}{1}'.format(url, file_name), path=g_p_.HomePath, log=r'/tmp/systemstatus.log')
    if res:
        g_p_.finish_download = True

    return res


def recovery():
    # start unzip files

    g_p_.mostfun.state = 'updating'
    logger.info('sh /etc/mountupdate.sh')
    subprocess.call('sh /etc/mountupdate.sh', shell=True,
                    stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    logger.info('rm -fr /update/*')
    subprocess.call('rm -fr /update/*', shell=True,
                    stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    cmd = 'tar -xf {0}{1} -C {2}'.format(g_p_.HomePath, 'toFlash.tar.gz', r'/update/')
    logger.info(cmd)
    p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    p.wait()
    if len(p.stdout.readlines()) > 0:
        g_p_.mostfun.state = 'ready'
        logger.warninging('update system failed: unzip system package failed')
        return False

    # start restart
    logger.info('update system: start reboot')
    sleep(1)
    subprocess.call('reboot ota', shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
