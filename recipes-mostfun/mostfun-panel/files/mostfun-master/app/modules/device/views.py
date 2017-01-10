#!/usr/bin/env python
# coding: utf-8
'''

'''
import math
import os
import re
import platform
import subprocess
import shutil
from datetime import datetime as dt

from flask import json, send_from_directory, render_template, request, jsonify

from app.modules.device.printer import mostfun
from app.modules.filemgr import FileManage
from app.modules.utils.Utils import getINI, modINI
from . import device
from ..utils import login_required_, mobile_detector, mail
from ... import g_p_, logger

__author__ = 'Jux.Liu'

sysstr = platform.system()
# 检测平台，指定相关路径
g_p_.mostfun = mostfun()
g_p_.mostfun.reset()


@device.route('/send/<command>/')
@login_required_
def send(command):
    """
向设备发送操纵命令
    :param command: 命令
    :return: String: 错误信息/ done
    """
    command = [command]
    if g_p_.mostfun.send_command(command):
        res = 1
    else:
        res = 31

    return json.dumps({'code': res})


@device.route('/cmd_msg/')
@login_required_
def cmdMsg():
    return json.dumps({'result': g_p_.mostfun.web_box_getter()})


@device.route('/device/state/')
def getState():
    """
获取当前的打印状态
    :return:
    """
    state = g_p_.mostfun.get_state()
    detail = ''
    if state == 'ready':
        printer_mesgs = g_p_.mostfun.env_box_getter()
        # if len(printer_mesgs)>0:
        #     print_info = printer_mesgs.pop().split(';')
        #     if print_info[0] == "taskfinished":
        #         finishSendMail(print_info)

    else:
        fileName = os.path.basename(g_p_.mostfun._filePath)
        layerCount = g_p_.mostfun._g.layerCount
        layerNum = g_p_.mostfun._g.layerNum
        percent = g_p_.mostfun.get_percent()
        detail = {'fileName': fileName,
                  'layerCount': layerCount,
                  'layerNum': layerNum,
                  'percent': percent}

    return json.dumps({'result': True, 'msg': {'state': state, 'details': detail}})


@device.route('/device/temperature/')
@login_required_
def getTemper():
    alltempdata = {'extTemp': '%d' % g_p_.mostfun.get_extruderTemp(),
                   'bedTemp': '%d' % g_p_.mostfun.get_bedTemp(),
                   'extTargetTemp': '%d' % g_p_.mostfun.get_extruderTargetTemp(),
                   'bedTargetTemp': '%d' % g_p_.mostfun.get_bedTargetTemp()}
    return json.dumps(alltempdata)


def find_gcode(filename, path=g_p_.Flash + g_p_.GcodePath):
    """
    判断文件是否存在
    :param filename:文件名
    :param path: 文件路径
    :return: True/False
    """
    filelocal = (os.path.join(path, filename).encode(
        encoding='UTF-8', errors='strict'))
    return os.path.exists(filelocal)


def get_filesize(filename, path):
    """
    获取文件的大小
    :param filename: 文件名
    :param path: 路径
    :return:文件大小(字节)
    """
    filelocal = os.path.join(path, filename.encode(
        encoding='UTF-8', errors='strict'))
    return os.path.getsize(filelocal.encode(encoding='UTF-8', errors='strict'))


def runcura(filename, src, target='/home/mostfuncp/gcode/'):
    """
    cura切片引擎执行
    :param filename: 源文件名
    :param src: 源文件路径
    :param target: 目标文件路径
    :return:
    """
    (filename, ext) = os.path.splitext(filename)
    filename += ".gcode"
    src = src.encode(encoding='UTF-8', errors='strict')
    target = (os.path.join(target, filename)).encode(
        encoding='UTF-8', errors='strict')
    process = "/mostfun/slicer/CuraEngine '%s' -o '%s' -c /mostfun/slicer/default.cfg" % (
        src, target)
    subprocess.call(process, shell=True, stderr=subprocess.PIPE,
                    stdout=subprocess.PIPE)


@device.route('/print_check/', methods=['POST'])
@login_required_
def print_check():
    """
    打印文件状态检查
    """
    local = {
        0: g_p_.Flash + g_p_.GcodePath,
        1: g_p_.SDCard,
        2: g_p_.USB,
        3: g_p_.Flash + g_p_.PausedPath,
        4: g_p_.Flash + g_p_.ModelPath
    }

    if g_p_.mostfun.state not in ['ready', 'pause']:
        return jsonify({
            'status': 'error',
            'code': 37
        })
    data = request.get_json()
    location = local[data['path']]
    (filename, ext) = os.path.splitext(data['filename'])
    if find_gcode(filename=filename + ".gcode", path=location):
        return jsonify({
            "status": "print",
            "content": {
                "filename": filename + ".gcode",
                "path": location
            }
        })
    else:
        if ext.lower() == ".stl":
            location = local[4]
            return jsonify({
                "status": "runcura",
                "content": {
                    "filename": data['filename'],
                    'path': location
                }
            })
        else:
            return jsonify({
                "status": "error",
                "content": ""
            })


@device.route('/runcura/', methods=['POST'])
@login_required_
def stlcut():
    """
    切片操作路由
    """
    location = g_p_.Flash + g_p_.GcodePath
    data = request.get_json("content")
    (filename, ext) = os.path.splitext(
        data['filename'].encode(encoding='UTF-8', errors='strict'))
    # 判断文件大小
    res = get_filesize(filename=data["filename"], path=data[
        'path']) > 10485760
    if res:
        return jsonify({
            "status": "error",
            "code": 43
        })
    else:
        runcura(filename=data['filename'],
                src=os.path.join(data['path'], data['filename'].encode(encoding='UTF-8', errors='strict')))
        return jsonify({
            "status": "print",
            "content": {
                "filename": filename + ".gcode",
                "path": location
            }
        })


@device.route('/print-test/', methods=['POST'])
@login_required_
def print_test():
    """
    打印操作
    :return:
    """
    data = request.get_json('content')
    res = 2 if data['path'] != 'g_p_.PausedPath' else 3
    if find_gcode(data['filename'], data['path']):
        localfile = (os.path.join(data['path'], data['filename'])).encode(
            encoding='UTF-8', errors='strict')
        if g_p_.mostfun.beginTask(localfile):
            return json.dumps({'code': 1})
        else:
            return json.dumps({'code': res})


@device.route('/print/', methods=['POST'])
@login_required_
def toPrint():
    """
打印操作
    :param GcodeFileName:
    :return:
    """
    # g_p_.mostfun.state = 'ready'  # 纯软件调试时解开注释
    if g_p_.mostfun.state not in ['ready', 'pause']:
        return json.dumps({'code': 37})
    data = request.get_json()
    ua = request.headers.get('User-Agent')
    if mobile_detector.process_request(ua):
        logger.info('printed by mobile browser')
    else:
        logger.info('printed by normal browser')

    model_type = data['path']
    (filename, ext) = os.path.splitext(data["filename"])
    filename = filename.encode(encoding='UTF-8', errors='strict')
    if model_type != 3:
        logger.info('start task')

        if model_type == 0:
            if ext.lower() == ".gcode":
                location = g_p_.Flash + g_p_.GcodePath
            elif ext.lower() == ".stl":
                location = g_p_.Flash + g_p_.ModelPath

        elif model_type == 1:
            location = g_p_.SDCard

        elif model_type == 2:
            location = g_p_.USB

        res = 2
    else:
        logger.info('continue task')
        location = g_p_.PausedPath
        res = 3
    if ext.lower() == ".stl" and not find_gcode(filename=filename + ".gcode"):
        # 判断文件大小(10M)
        if get_filesize(filename=data["filename"], path=location) > 10485760:
            return json.dumps({"code": 43})
        else:
            runcura(filename=filename,
                    src=os.path.join(location, data['filename'].encode(encoding='UTF-8', errors='strict')))
    filename += ".gcode"
    if model_type == 0:
        location = g_p_.Flash + g_p_.GcodePath

    if find_gcode(filename, location):
        if g_p_.mostfun.beginTask(os.path.join(location, filename.encode(encoding='UTF-8', errors='strict'))):

            return json.dumps({'code': 1})
        else:
            return json.dumps({'code': res})


@device.route('/pause/')
@login_required_
def pause():
    """
暂停打印动作
    :param: null
    :return:
    """
    logger.info('pause task')
    g_p_.mostfun.pauseTask()
    return json.dumps({'code': 1})


@device.route('/resume/')
@login_required_
def resume():
    """
恢复打印动作
    :param: null
    :return:
    """
    logger.info('resume task')
    g_p_.mostfun.resumeTask()
    return json.dumps({'code': 1})


@device.route('/reset/', methods=['GET', 'POST'])
@login_required_
def reset():
    """
强制停机操作
    :param: null
    :return:
    """
    # reset功能只在Linux上生效，详见models.py
    logger.warning('reset printer')
    g_p_.mostfun.reset()

    # del m
    # m = mostfun('/dev/ttyMFD1')
    # models.Init()
    return json.dumps({'code': 1})


@device.route('/cancel/', methods=['GET', 'POST'])
@login_required_
def cancel():
    """
强制停机操作
    :param: null
    :return:
    """
    logger.warning('cancel task')
    g_p_.mostfun.cancelTask()
    return json.dumps({'code': 1})


@device.route('/save-task/', methods=['GET', 'POST'])
@login_required_
def save():
    logger.info('save task')
    g_p_.mostfun.stop_saveTask()
    return json.dumps({'code': 1})


@device.route('/cancel-task/', methods=['GET', 'POST'])
@login_required_
def cancelTask():
    logger.warning('cancel task')
    filename = request.get_json()['filename']
    if FileManage().delFile(filename, flag=0):
        return json.dumps({'code': 1})
    else:
        return json.dumps({'code': 9})


@device.route('/model/', methods=['POST', 'GET'])
@login_required_
def getModel():
    """

    :param FileName:
    :return:
    """
    data = request.get_json()
    FileName = data['filename']
    folder = g_p_.folder[data['path']]

    ext = FileName.split('.')[-1]
    if ext == 'stl' or ext == 'obj':
        if (data['path'] == 0):
            folder += g_p_.ModelPath
    # elif ext == 'jpg' or ext == 'png':
    #     folder += g_p_.ModelImgPath']
    elif ext == 'gcode':
        if (data['path'] == 0):
            folder += g_p_.GcodePath

    fn = ''
    li = os.listdir(folder)
    for item in li:
        if FileName == item.lower():
            fn = '{0}{1}'.format(folder, item)
            FileName = item
            break
        else:
            continue

    if os.path.exists(fn):
        sz = '%.2f' % (os.path.getsize(fn) / math.pow(1024, 2))
        if float(sz) > 20.0:
            return json.dumps({'code': 11})
        else:
            return send_from_directory(folder, FileName.decode('string-escape'))
    else:
        return json.dumps({'code': 10})


@device.route('/UI/<Button>/')
@login_required_
def LCDControl(Button):
    if Button is None:
        return
    controlList = {'L': '', 'R': '', 'D': '', 'DL': '', 'DR': '', 'DD': ''}
    return controlList[Button]


def shotpic():
    """
拍照动作
    :return:
    """
    import subprocess
    subprocess.call('echo \'0\' > /tmp/webcom', shell=True,
                    stdout=subprocess.PIPE, stderr=subprocess.STDOUT)


@device.route('/snapshot/')
def snapshot():
    shotpic()
    if not os.path.exists(r'/tmp/0.jpg'):
        logger.error('pic file not found')
    elif os.path.getsize(r'/tmp/0.jpg') == 0.0:
        logger.error('pic file size is 0')
    elif (dt.utcnow() - dt.utcfromtimestamp(os.stat(r'/tmp/0.jpg').st_ctime)).seconds > 1000:
        logger.error('camera down')
    else:
        return send_from_directory(r'/tmp/', '0.jpg', mimetype='application/octet-stream')

    return send_from_directory(r'/tmp/', 'default.jpg', mimetype='application/octet-stream')


@device.route('/webcam/')
def webcam():
    logger.info('webcam called')
    return render_template('webcam.html')


@device.route('/auto-leveling/')
@login_required_
def leveling():
    logger.info('web auto-leveling')
    return json.dumps({'code': 1 if g_p_.mostfun.auto_leveling() else 37})


@device.route('/take-photo/')
@login_required_
def takePic():
    """
拍照并发送邮件
    :return:
    """
    try:
        for item in range(0, 2):
            shotpic()
    except Exception as e:
        return json.dumps({'code': 13})

    res = False
    times = 0
    while not res and times < 2:
        res = mail.send_mail(title='Real time shot', content='Real time shot of your printing schedule',
                             attachments=r'/tmp/0.jpg')
        times += 1

    if res:
        logger.info('take photo and send ok')
        return json.dumps({'code': 1})
    elif res is None:
        return json.dumps({'code': 15})
    else:
        logger.error('take photo failed: send mail failed')
        return json.dumps({'code': 14})


@device.route('/reset-machine/')
@login_required_
def resetMachine():
    localconf = os.path.join(g_p_.LocalPath, "config.ini")
    origconf = os.path.join(g_p_.LocalPath, "config.orig")
    backupconf = os.path.join(g_p_.cfgbak, "config.ini")
    opkg = "/etc/opkg/"
    if os.path.exists(localconf):
        os.remove(localconf)
    if os.path.exists(backupconf):
        os.remove(backupconf)
    shutil.copy(origconf, localconf)
    for item in os.listdir(opkg):
        if re.search('myfeeds*', item):
            os.remove(os.path.join(opkg, item))
    logs = os.listdir(g_p_.log)
    if logs:
        for log in logs:
            os.remove(os.path.join(g_p_.log + log))
    # return render_template('reset-machine.html')
    return "ok"


@device.route('/device/reset/')
@login_required_
def user_reset():
    """
    用户重置机器接口
    :return:
    """
    lastcheck = getINI(section="other", option='lastcheck')
    lastupdate = getINI(section='other', option='lastupdate')
    printedsecs = getINI(section='other', option='printedsecs')
    subprocess.call(r'/mostfun/panel/reset.sh', shell=True,
                    stderr=subprocess.PIPE, stdout=subprocess.PIPE)
    try:
        modINI(section="other", option='lastcheck', value=lastcheck)
        modINI(section="other", option='lastupdate', value=lastupdate)
        modINI(section="ohter", option='printedsecs', value=printedsecs)
    except:
        pass
    return render_template('reset-machine.html')


@device.route('/restart-panel/')
@login_required_
def restartMachine():
    subprocess.call(r'systemctl restart mostfun_panel', shell=True,
                    stderr=subprocess.PIPE, stdout=subprocess.PIPE)
