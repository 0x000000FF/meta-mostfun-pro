#!/usr/bin/env python
# coding: utf-8
'''
文件管理
所有方法的返回值均为 {"msg": msg, "result": result}形式，传送到页面需要转换为JSON字符串
'''
import hashlib
import urllib
import time

import subprocess

__author__ = 'Jux.Liu'

import os
import shutil
import zipfile
import glob
from zipfile import *

from ... import g_p_, logger


class FileManage():
    def __init__(self):
        pass

    __ALLOWED_EXTENSIONS = set(
        ['gcode', 'stl', 'obj', 'jpg', 'jpeg', 'png', 'gif', 'zip', '7z', 'rar', 'tar', 'gz', 'bz2'])

    def _allowed_file(self, filename):
        """
检测可以允许上传和下载的文件格式
        :param filename:
        :return: 文件格式后缀名字符串
        """
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in self.__ALLOWED_EXTENSIONS

    def searchFile(self, pattern='.*', base=".", circle=True):
        """
查找文件
        :param pattern: 匹配文件类型
        :param base: 查找路径
        :param circle: 是否递归查找
        :return: {'result': boolean, 'msg': String}: result-True成功，False失败; msg: 结果信息
        """
        if base == ".":
            base = os.getcwd()

        final_file_list = []
        cur_list = os.listdir(base)
        for item in cur_list:
            full_path = os.path.join(base, item)

            if item == ".svn":
                continue

            if full_path.endswith(".doc") or \
                    full_path.endswith(".bmp") or \
                    full_path.endswith(".wpt") or \
                    full_path.endswith(".dot"):
                continue

            if os.path.isfile(full_path):
                if full_path.endswith(pattern):
                    # 路径
                    pathname = os.path.dirname(full_path)
                    # 文件名
                    filename = os.path.basename(full_path)
                    # 创建时间
                    create_time = os.path.getctime(full_path)
                    # 文件大小
                    fsize = os.path.getsize(full_path)
                    dict1 = dict(filename=str(filename), pathname=str(
                        pathname), create_time=create_time, size=fsize)
                    final_file_list.append(dict1)
            else:
                if circle:
                    final_file_list += FileManage().searchFile(pattern, full_path, circle)

        return final_file_list

    def delFile(self, fileName, location=g_p_.Flash, flag=1):
        """
删除指定文件
        :param fileName: 文件名称
        :raise Exception: 错误信息
        :return: {'result': boolean, 'msg': String}: result-True成功，False失败; msg: 结果信息
        """
        wrongtime = 0
        result = True
        msg = ''

        def _del(fileName):
            global wrongtime
            global msg
            if os.path.exists(fileName):
                try:
                    os.remove(fileName)
                except Exception as e:
                    msg = os.remove(fileName)

                    wrongtime += 1

        srcFileName = fileName.encode(encoding='UTF-8', errors='strict')
        if flag == 1:
            for fileName in (location + g_p_.GcodePath + srcFileName + '.gcode',
                             location + g_p_.GcodePath + srcFileName + '.info',
                             location + g_p_.ModelPath + srcFileName + '.stl',
                             location + g_p_.ModelPath + srcFileName + '.info',
                             location + g_p_.ModelImgPath + srcFileName + '.jpg'):
                _del(fileName)
                continue

        elif flag == 0:
            fileName = location + g_p_.PausedPath + srcFileName + '.gcode'
            _del(fileName)

        if wrongtime != 0:
            result = False

        logger.info('delete file: {0} ok'.format(srcFileName))

        return result

    def zipFile(self, srcPath, srcFile, tarPath, tarFile):
        """
将指定路径的文件打包成zip文件
        :param srcPath: 文件来源路径
        :param srcFile: 文件名
        :param tarPath: zip文件存放路径
        :param tarFile: zip文件名称
        :return: {'result': boolean, 'msg': String}: result-True成功，False失败; msg: 结果信息
        """
        result = False
        msg = ''
        try:
            f = zipfile.ZipFile(tarPath + tarFile, 'a',
                                compression=zipfile.ZIP_DEFLATED)
            # 第二个参数写上时，压缩包内只包含文件，不写时会包含上层文件夹
            f.write(filename=srcPath + srcFile, arcname=srcFile,
                    compress_type=zipfile.ZIP_DEFLATED)
        except Exception as err:
            msg = err
        else:
            result = True
        finally:
            f.close()

        return {'result': result, 'msg': msg}

    def zipDir(self, srcPath, srcDir, tarPath, tarFile):
        """
将指定路径的文件夹及其内部文件打包成zip文件
        :param srcPath:
        :param tarPath:
        :param tarFile:
        :return: {'result': boolean, 'msg': String}: result-True成功，False失败; msg: 结果信息
        """
        result = False
        msg = ''
        try:
            f = zipfile.ZipFile(tarPath + tarFile, 'a',
                                compression=zipfile.ZIP_DEFLATED)
            startdir = srcPath + srcDir
            # 便利文件夹下的所有文件和子文件夹，放入打包好的zip文件
            for dirpath, dirnames, filenames in os.walk(startdir):
                for filename in filenames:
                    f.write(os.path.join(dirpath, filename),
                            compress_type=zipfile.ZIP_DEFLATED)
        except Exception as err:
            msg = err
        else:
            result = True
        finally:
            f.close()

        return {'result': result, 'msg': msg}

    def unZip(self, srcPath, srcZip, tarPath):
        """
解压zip文件到指定路径
        :param srcPath: zip文件路径
        :param srcZip: zip文件名称
        :param tarPath: 解压到的目标路径
        :return: {'result': boolean, 'msg': String}: result-True成功，False失败; msg: 结果信息
        """
        result = False
        msg = ''
        f_handle = None
        myzip = None
        try:
            myzip = ZipFile(srcPath + srcZip)
            # 根据名称中所带的'/'数量顺序排序，避免出现子文件夹未创建导致解压失败的问题
            myfilelist = sorted(myzip.namelist(), key=lambda x: ('/' and x))
            for name in myfilelist:
                if name.endswith('/'):
                    os.mkdir(os.path.join(tarPath, name))
                    myfilelist.remove(name)
                else:
                    f_handle = open(os.path.join(tarPath, name), "wb")
                    f_handle.write(myzip.read(name))
        except Exception as err:
            msg = err
        else:
            result = True
        finally:
            f_handle.close()
            myzip.close()
        return {'result': result, 'msg': msg}

    def uploadFile(self, file):
        """
上传文件到指定的文件夹
        :param file: 需要上传的文件--FileStorage类型
        :return: {'result': boolean, 'msg': String}: result-True成功，False失败; msg: 结果信息
        """
        result = False
        msg = ''
        folder = ''
        filename = file.filename.encode(
            encoding='UTF-8', errors='strict').split('.')
        ext = filename.pop().lower()
        filename = ''.join(filename) + '.' + ext
        flag = True
        logger.info('upload file: {0}'.format(filename))

        if file and self._allowed_file(filename):
            folder = g_p_.Flash
            if ext in ('stl', 'obj'):
                folder += g_p_.ModelPath

            elif ext in ('jpg', 'jpeg', 'png', 'gif'):
                folder += g_p_.ModelImgPath

            elif ext == 'gcode':
                folder += g_p_.GcodePath

            elif ext in ('zip', '7z', 'rar', 'tar', 'gz'):
                unzip_folder = self.mkdir4Unzip()

                folder += g_p_.ModelZipPath
                file.save(os.path.join(folder, filename))
                flag = False
                self.unZip(folder, filename, unzip_folder)
                file_list = os.listdir(unzip_folder)

                for f in file_list:
                    self.moveFile(f, unzip_folder)
                logger.info('unzip file: {0} ok'.format(filename))

            if flag:
                file.save(os.path.join(folder, filename))
            result = True
            logger.info('upload file finished')
        else:
            logger.warning('file is not allowed to update')

        return result

    def moveFile(self, filename, unzip_folder):
        """
分配解压后的文件到对应文件夹
        :param filename: 解压后的文件名
        :param unzip_folder: 解压路径
        :return:
        """
        ext = filename[filename.rfind('.'):]
        the_file = unzip_folder + '/' + filename
        the_path = g_p_.Flash
        move_flag = True

        if ext in ('.stl', '.obj'):
            the_path += g_p_.ModelPath

        elif ext in ('.jpg', '.jpeg', '.png', '.gif'):
            the_path += g_p_.ModelImgPath

        elif ext == '.gcode':
            the_path += g_p_.GcodePath

        else:
            move_flag = False

        if move_flag:
            shutil.copy(the_file, the_path)

    def downloadFile(self, url, path, log):
        subprocess.call('wget -c -P {path} {url} -a {log}'.format(path=path, url=url, log=log), shell=True,
                        stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        return True

    def downloadFiles(self, url, path):
        """
文件下载
        :param url:指定下载地址
        :param path:指定文件存储路径
        :return: {'result': boolean, 'msg': String}: result-True成功，False失败; msg: 结果信息
        """
        name = url.split('/')[-1]
        local = os.path.join(path, name)
        try:
            logger.info('start download file from: {0}'.format(url))
            urllib.urlretrieve(url, local, self.cbk)
            result = True
        except:
            result = False
        logger.info('file download result: {0}'.format(result))
        return result

    """
    cbk为回调函数，用于显示当前的下载状态，可要可不要
    """

    def cbk(self, downloadBlock, blockSize, fileSize):
        """
本函数为downloadFile中urlretrieve的回调函数，用于返回下载的实时情况，可选
        :param downloadBlock:已经下载的数据块
        :param blockSize: 数据块的大小
        :param fileSize: 远程文件的大小
        :return: 无（仅仅只是下载状态的反馈）
        """
        per = 100.0 * downloadBlock * blockSize / fileSize
        if per > 100:
            per = 100
        print("%.f%%" % per)
        with open(r'/tmp/systemstatus.log', 'w') as f:
            f.write(str(per))

    def generate_file_md5(self, filename):
        logger.info('start calculate md5')
        md5 = hashlib.md5()
        with open(filename, "rb") as f:
            for chunk in iter(lambda: f.read(128 * md5.block_size), b''):
                md5.update(chunk)
        md5 = md5.hexdigest()
        logger.info('md5: {0}'.format(md5))
        return md5

    def check_md5(self, fileName, md5str):
        logger.info('start check md5')
        if md5str.strip() == self.generate_file_md5(fileName).strip():
            logger.info('md5 match')
            return True
        else:
            logger.warning('md5 not match')
            return False

    def mkdir4Unzip(self):
        """
创建解压文件夹
        :return: 返回文件夹路径
        """
        ISOTIMEFORMAT = '%Y%m%d%H%M%S'
        unzip_folder = g_p_.Flash + g_p_.TmpFolder + \
            str(time.strftime(ISOTIMEFORMAT))
        os.mkdir(unzip_folder)
        return unzip_folder


def get_file(path):
    """
    获取某一文件夹下的所有文件
    :param path: 文件夹路径
    :return: 文件列表
    """
    result = glob.glob(path)
    return result


def get_files_list(flash_path, file_ext):
    """
    获取指定类型的文件列表
    :param flash_path: 本地文件夹路径
    :param file_ext: 文件后缀
    :return: 文件列表
    """
    result = map(lambda item_path, ext=file_ext: get_file(
        path=g_p_.Flash + item_path + ext), flash_path)
    flash = []
    for item in result:
        flash.extend(item)
    sd = get_file(g_p_.SDCard + file_ext)
    usb = get_file(g_p_.USB + file_ext)
    filePathList = {0: flash, 1: sd, 2: usb}
    return filePathList