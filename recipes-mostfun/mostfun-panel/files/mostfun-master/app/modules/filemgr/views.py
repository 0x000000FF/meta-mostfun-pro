#!/usr/bin/env python
# coding: utf-8
'''

'''
import glob
import json
import os
import time

from flask import request

from app import g_p_, logger
from . import filemgr, FileManage
from FileManage import get_files_list
from ..utils import login_required_

__author__ = 'Jux.Liu'


@filemgr.route('/upload-file/', methods=['GET', 'POST'])
@login_required_
def upload():
    """
上传文件动作
    :param: null
    :return:
    """
    if request.method == 'POST':
        print(request.files)
        files = request.files['file']
        # fm=FileManage()
        # return fm.uploadFile(file)
        res = FileManage().uploadFile(files)
        return json.dumps({'code': 1 if res else 16})


def delFile(FileName, location):
    FileName = FileName.split("\\")[-1].split(".")[0]

    return FileManage().delFile(FileName, location)


@filemgr.route('/del/', methods=['POST', 'GET'])
@login_required_
def delsFile():
    """
删除文件
    :return:
    """
    failcount = list()
    if request.method == "POST":
        filelist = request.get_json()
        for item in filelist:
            filename = item['filename']
            path = g_p_.folder[item['path']]
            dr = delFile(filename, path)
            if dr:
                continue
            else:
                failcount.append(item)
    if len(failcount) == 0:
        logger.info('delete file fail {0}'.format(failcount))
    return json.dumps({'code': 1})


@filemgr.route('/del-log/', methods=['POST'])
@login_required_
def delLog():
    filename = request.get_json()['filename']
    try:
        os.remove(r'/home/logs/' + filename)
        return json.dumps({'code': 1})
    except:
        return json.dumps({'code': 17})


@filemgr.route('/file/filelist/<string:ext>/')
@login_required_
def getFileList(ext):
    """
获取文件列表
    :return:
    """
    if ext == 'gcode':
        flash_path = [g_p_.GcodePath]
        file_ext = "*.gcode"
    elif ext == 'stl':
        flash_path = [g_p_.ModelPath]
        file_ext = "*.stl"
    else:
        flash_path = [g_p_.GcodePath, g_p_.ModelPath,
                      g_p_.ModelImgPath, g_p_.ModelZipPath]
        file_ext = "*"
    filePathList = get_files_list(flash_path=flash_path, file_ext=file_ext)
    fileInfoTable = list()
    for k, v in filePathList.items():
        path = k
        for filePath in v:
            fileName = os.path.basename(filePath.decode('utf-8'))
            fileContent = 'mostfun model'
            fileSize = "%.2f" % (os.path.getsize(filePath) / 1024.0 / 1024.0)
            fileTime = time.strftime(
                '%Y/%m/%d %H:%M', time.localtime(os.path.getctime(filePath)))
            fileInfoList = {'fileName': fileName, 'fileContent': fileContent, 'fileSize': fileSize,
                            'fileTime': fileTime, 'path': path}
            fileInfoTable.append(fileInfoList)

    return json.dumps(fileInfoTable)


@filemgr.route('/file/backlist/')
@login_required_
def getBackList():
    back = glob.glob(g_p_.Flash + g_p_.PausedPath + '*.gcode')
    fileInfoTable = list()
    for filePath in back:
        fileName = os.path.basename(filePath).decode('utf-8')
        fileTime = time.strftime(
            '%Y/%m/%d %H:%M', time.localtime(os.path.getctime(filePath)))
        fileSize = "%.2f" % (os.path.getsize(filePath) / 1024.0 / 1024.0)
        fileInfoList = {'fileName': fileName,
                        'fileTime': fileTime, 'fileSize': fileSize}
        fileInfoTable.append(fileInfoList)

    return json.dumps(fileInfoTable)
