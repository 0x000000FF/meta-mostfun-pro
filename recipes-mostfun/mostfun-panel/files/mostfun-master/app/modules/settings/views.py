#!/usr/bin/env python
# coding: utf-8
'''

'''
import json
import os
import shutil
import subprocess
import time
from datetime import datetime
from os import remove

from flask import request, session, current_app, render_template
from urllib2 import urlopen
from app import g_p_, logger, CDN_list
from app.modules.device import wifi4edison
from app.modules.filemgr import FileManage
from app.modules.utils.Utils import getINI, modINI
from config import Config
from . import settings
from ..user.models import User
from ..utils import login_required_, Update, mail

__author__ = 'Jux.Liu'

config = Config()


@settings.route('/get-version/')
def get_version():
    """
获取当前系统的版本信息
    :return:
    """
    pv = current_app.config['CP_VERSION']
    sv = current_app.config['SYS_VERSION']
    lu = getINI('other', 'lastupdate')
    lc = getINI('other', 'lastcheck')
    if pv is not None and sv is not None:
        return json.dumps({'panel': pv, 'system': sv, 'lastupdate': lu, 'lastcheck': lc})
    else:
        return json.dumps({'code': 18})


@settings.route('/get-mail-setting/')
def get_mail_setting():
    """
获取邮件设置
    :return:
    """
    param = mail.get_config()
    param['mail_enabled'] = getINI('mail', 'enabled')
    if param is None or len(param) != 8:
        return json.dumps({'code': 19})
    param['code'] = 1
    return json.dumps(param)


@settings.route('/change-password/', methods=['GET', 'POST'])
@login_required_
def changePwd():
    """
修改设备登陆密码
    :return:
    """
    old_password = request.get_json()['old_password']
    new_password = request.get_json()['new_password']
    rpt_password = request.get_json()['rpt_password']
    if rpt_password == new_password:

        user = User(session.get('id'), getINI(
            'user', 'password'))  # UserID通过session取
        pwd_res = user.changePassword(old_password, new_password)
        logger.info('change password result: {}'.format(pwd_res))

        if pwd_res:
            # todo: 发送的消息内容需要再做修改
            mail_res = mail.send_mail(
                title="Password changed", content="Your password has been changed.")
            logger.info(
                'change password send mail result: {}'.format(mail_res))
            return json.dumps({'result': True, 'msg': '/logout', 'code': 1})
    logger.info('change password error')
    return json.dumps({'code': 20})


@settings.route('/get-wireless-list/', methods=['POST', 'GET'])
@login_required_
def getWirelessList():
    """
修改设备无线配置
    :param: null
    :return: wireless.html
    """
    wifi_map = wifi4edison.scanForNetworks()
    if wifi_map:
        return json.dumps(wifi_map)
    else:
        return json.dumps('')


@settings.route('/get-current-wifi/', methods=['GET', 'POST'])
@login_required_
def getCurrWifi():
    try:
        wifi_info = wifi4edison.checkNetwork()
    except:
        wifi_info = {'code': 41}
    finally:
        return json.dumps(wifi_info)


@settings.route('/connect-wifi/', methods=['POST'])
@login_required_
def connect_wifi():
    """
连接或变更wifi
    :return:
    """
    ssid = request.get_json()['ssid']
    secure = request.get_json()['secure']
    password = request.get_json()['password']
    res = None
    try:
        connect = wifi4edison.configureNetwork(ssid, secure, password)
        res = wifi4edison.setNetwork(connect)
    except Exception as e:
        logger.error(e)
        res = {'code': 22}
    else:
        if res:
            res = wifi4edison.checkNetwork()
            logger.info('wifi changed')
        else:
            res = {'code': 39}
            # elif res == 0:
            #     res = {'code': 40}
    finally:
        return json.dumps(res)


@settings.route('/config-wpa/', methods=['POST'])
@login_required_
def config_wpa():
    ssid = request.get_json()['ssid']
    wpapsk = request.get_json()['password']
    result = False
    msg = ''
    if len(wpapsk) < 8:
        msg = 'password shuld longer than 8 characters.'
    else:
        subprocess.call("sed -i -e 's/^WPAPSK=.*/WPAPSK='{0}'/g' /etc/Wireless/RT2870AP/RT2870AP.dat".format(wpapsk),
                        shell=True)
        subprocess.call("sed -i -e 's/^SSID=.*/SSID='{0}'/g' /etc/Wireless/RT2870AP/RT2870AP.dat".format(ssid),
                        shell=True)
        subprocess.call("echo {0} > /etc/hostname".format(ssid), shell=True)
        subprocess.call('systemctl restart hostapd', shell=True,
                        stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        result = True

    return json.dumps({'code': 1 if result else 23})


@settings.route('/enable-email/', methods=['GET', 'POST'])
@login_required_
def mailEnable():
    res = {'code': 27}
    enabled = request.get_json()['enabled']
    if modINI(section='mail', option='enabled', value=enabled):
        res['code'] = 1
    return json.dumps(res)


@settings.route('/change-mail/', methods=['GET', 'POST'])
@login_required_
def changeMail():
    """
修改设备推送邮箱和接收推送的邮箱
    :return:
    """
    param = {"nickname": request.get_json()['nickname'],
             "password": request.get_json()['password'],
             "smtp_server": request.get_json()['smtp_server'],
             "prefix": request.get_json()['prefix'],
             "to_addr": request.get_json()['to_addr'],
             "from_addr": request.get_json()['from_addr'],
             'port': request.get_json()['port']}

    res = mail.change_config(params=param)

    # 这里必须写英文，否则会报错：'ascii' codec can't decode byte 0xe9 in position 0:
    # ordinal not in range(128)。推测是flask本身的问题。
    return json.dumps({'code': 1 if res else 26})


@settings.route('/test-mail/', methods=['POST'])
@login_required_
def testMail():
    res = mail.send_mail(title='Test Email', content='This is a test email')
    return json.dumps({'code': 1 if res else 36})


@settings.route('/getLang/')
def getLang():
    return json.dumps({'lang': getINI(section='other', option='lang')})


@settings.route('/setLang/', methods=['POST', 'GET'])
def setLang():
    lang = request.get_json()['lang']
    res = modINI(section='other', option='lang', value=lang)
    return json.dumps({'code': 1 if res else 29})


@settings.route('/chk-update/')
@login_required_
def chkUpdate():
    """
检查更新
    :return:
    """
    newestPackage = chkTime()
    if newestPackage > 0:
        lastupdate = time.mktime(time.strptime(
            getINI('other', 'lastupdate'), '%Y-%m-%d %H:%M:%S'))
        if lastupdate > newestPackage:
            pass
        else:
            return json.dumps(chkUpdateList())
    else:
        return json.dumps({'code': 24})


def chkTime():
    cdn = getINI('other', 'cdn')
    cdnurl = CDN_list[cdn]
    import re
    try:
        resp = urlopen(cdnurl)
        html = resp.read()
        link_list = re.findall(r"(?<=  )[0-9].+?[0-9](?=  )", html)
        max_t = 0
        for url in link_list:
            t = time.mktime(time.strptime(url, "%d-%b-%Y %H:%M"))
            if (t > max_t):
                max_t = t
        return max_t
    except:
        return -1


def chkUpdateList():
    old_state = g_p_.mostfun.get_state()
    g_p_.mostfun.state = 'checking'
    modINI('other', 'lastcheck', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    res = Update.check_sys_update()
    g_p_.package_list['data'] = res
    if res == ['No Update']:
        g_p_.package_list['data'] = None
    g_p_.mostfun.state = old_state
    return {'data': res}


@settings.route('/get-package-list/')
@login_required_
def packageList():
    return json.dumps(g_p_.package_list)


@settings.route('/get-download-progress/')
def getDownloadProcess():
    """
获取更新包的下载进度
    :return:
    """
    is_download_finish = False
    if g_p_.update_list['opkg_update']:
        update_type = 'opkg'
        ipks = []
        finished_ipks = []

        if os.path.exists(r'/tmp/wgetstatus.log'):
            with open(r'/tmp/wgetstatus.log') as f:
                info = f.readlines()

                for item in info:
                    if 'http://update.mostfun.cc' in item and '.ipk' in item:
                        ipks.append(item)
                    if '.ipk' in item and 'saved' in item:
                        finished_ipks.append(item)

                if '%' in info[-2]:
                    g_p_.download_process = info[-2].lstrip().split()[6]

        ipk_name = ipks[-1].split('/')[-1]
        if len(finished_ipks) == g_p_.update_packages_num:
            is_download_finish = True

    if g_p_.update_list['system_update']:
        update_type = 'system'
        ipk_name = config.SYS_VERSION.strip()

        with open(r'/tmp/systemstatus.log') as f:
            info = f.readlines()
            if '%' in info[-2]:
                g_p_.download_process = info[-2].lstrip().split()[6]
                # print('--- ', g_p_.download_process)

        if g_p_.finish_download:
            is_download_finish = True

    # print({'ipk_name': ipk_name, 'download_process': g_p_.download_process, 'is_finish': is_download_finish, 'update_type': update_type})

    return json.dumps({'ipk_name': ipk_name, 'download_process': g_p_.download_process,
                       'is_finish': is_download_finish, 'update_type': update_type})


@settings.route('/set-time-zone/', methods=['POST'])
def setTimeZone():
    """
设置时区
    :return:
    """
    ZONE = {"+": "-", "-": "+"}
    zone_num = request.get_json()['timezone']
    zone_num = ZONE[zone_num[0]] + zone_num[1:]
    subprocess.call('rm /etc/localtime', shell=True)
    info = 'ln -s /usr/share/zoneinfo/Etc/GMT{0} /etc/localtime'.format(
        zone_num)
    subprocess.call(info, shell=True)
    return json.dumps({'code': 1})


@settings.route('/get-time-zone/')
def getTimeZone():
    p = subprocess.Popen("date", shell=True,
                         stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    p.wait()
    t = p.stdout.readlines()[0].split(' ')
    timezone = ''
    for timezone in t:
        if timezone.startswith('UTC'):
            timezone = '0'
            break
        elif timezone.startswith('GMT'):
            timezone = timezone.split('GMT')[1].strip()
            break
        else:
            continue
    return json.dumps({"code": 1, "res": timezone or '0'})


@settings.route('/waiting-update/')
def waitUpdate():
    return render_template('waitingUpdate.html')


@settings.route('/do-update/')
@login_required_
def doUpdate():
    """
进行更新操作
    :return:
    """
    res = {'code': 25}
    if g_p_.mostfun.state not in ['ready', 'error']:
        pass

    else:
        old_state = g_p_.mostfun.get_state()
        modINI('other', 'lastupdate',
               datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        result = Update.start_update()
        if result:
            res = {'code': 1}
        g_p_.mostfun.state = old_state if old_state != 'updating' else 'ready'
    return json.dumps(res)


def get_space():
    """
    获取存储空间值
    :return （'total', 'used')
    """
    p = subprocess.Popen('df | grep /mmcblk0p10', shell=True,
                         stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    data = p.stdout.readline().split()
    p.terminate()
    return (data[1], data[2])


@settings.route('/space-left/')
@login_required_
def spaceLeft():
    (total, used) = get_space()
    return json.dumps({'total': total, 'used': used})


@settings.route('/recovery/<string:password>')
def admin_recovery(password):
    # update from the dev server
    pass


@settings.route('/recovery/')
def recovery():
    old_state = g_p_.mostfun.get_state()
    g_p_.mostfun.state = 'updating'
    if Update.copy_new_system_file():
        return json.dumps(Update.recovery())
    else:
        g_p_.mostfun.state = old_state
        return json.dumps({'code': 38})


@settings.route('/get-cdn/')
def get_cdn():
    cdn = getINI('other', 'cdn')
    cdn_detail = ''
    if cdn == 'my':
        with open(r'/etc/opkg/myfeeds') as f:
            cdn_detail = f.readline()
    if len(cdn):
        return json.dumps({'code': 1, 'cdn': cdn, 'cdn_detail': cdn_detail})
    else:
        return json.dumps({'code': 32})


def testSpeed(url):
    """
CDN测速
    :param url: 需要测速的url地址
    :return:
    """
    sumSpan = 0.0
    for i in range(10):
        startTime = datetime.now()
        try:
            urlopen(url, timeout=10)
        except:
            pass
        endTime = datetime.now()
        span = (endTime - startTime).microseconds / 1000.0
        print(span)
        sumSpan = sumSpan + span

    return '%.0f' % (sumSpan / 10.0)


@settings.route('/change-cdn/<string:ip>/')
@login_required_
def changeCDN(ip):
    """
修改CDN设置
    :return:
    """
    # cdn = request.get_json()['cdn']
    if os.path.exists(r'/tmp/upgradelist.txt'):
        remove(r'/tmp/upgradelist.txt')
    else:
        pass
    if ip:
        with open(r'/etc/opkg/myfeeds', 'w') as f, open(r'/etc/opkg/my', 'w') as m:
            data = 'src allcn http://{ip}/all\nsrc i586cn http://{ip}/edison\nsrc core2-32cn http://{ip}/core2-32'.format(
                ip=ip)
            CDN_list['my'] = 'http://{ip}'.format(ip=ip)
            modINI('other', 'cdn', 'my')
            f.write(data)
            m.write(CDN_list['my'])
        shutil.copy('/etc/opkg/myfeeds', '/etc/opkg/myfeeds.conf')
        return json.dumps({'code': 1})
    else:
        return json.dumps({'code': 33})


@settings.route('/test-cdn/')
@login_required_
def testCDN():
    speed_list = {'cn': 0,
                  'hk': 0,
                  'eu': 0,
                  'us': 0}
    for item in CDN_list:
        speed_list[item] = testSpeed(CDN_list[item])
    return json.dumps(speed_list)


@settings.route('/export-log/', methods=['POST'])
@login_required_
def exportLog():
    file_list = request.get_json()['filename']
    fp = '{path}{file}'.format(file=file_list, path=g_p_.log)
    if os.path.exists(fp):
        with open(fp, 'r') as f:
            return json.dumps({'code': 1, 'res': f.readlines()})
    else:
        return json.dumps({'code': 42})
        # file_list_length = len(file_list)
        # if file_list_length == 0:
        #     return json.dumps({'code': 42})
        # elif file_list_length == 1:
        #     fp = '{path}{file}'.format(file=file_list[0], path=g_p_.log)
        #     if os.path.exists(fp):
        #         with open(fp, 'r', encoding='utf-8') as f:
        #             return json.dumps({'code': 1, 'res': f.read()})
        #     if os.path.exists('{path}{file}'.format(file=file_list[0], path=g_p_.log)):
        #         return send_from_directory(g_p_.log, file_list[0])
        #     else:
        #         return json.dumps({'code': 42})
        # elif file_list_length > 1:
        #     if os.path.exists(r'/tmp/logs/'):
        #         pass
        #     else:
        #         os.mkdir(r'/tmp/logs/')
        #     for item in file_list:
        #         shutil.copyfile('{path}{file}'.format(path=g_p_.log, file=item), r'/tmp/logs/')
        #     FileManage().zipDir(r'/tmp/', r'/logs/', r'/tmp/', 'logs.zip')
        #     return send_from_directory(r'/tmp/', 'logs.zip')

        # frontpage multi-select not working now, so stop this part


@settings.route('/clean-logs/')
@login_required_
def cleanLog():
    shutil.rmtree(r'/home/logs/')
    os.mkdir(r'/home/logs/')


@settings.route('/list-logs/')
@login_required_
def listLog():
    res = FileManage().searchFile(pattern='.log', base=g_p_.log)
    return json.dumps(res)
