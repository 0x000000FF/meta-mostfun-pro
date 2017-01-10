#!/usr/bin/env python
# coding: utf-8
'''

'''
import subprocess

import codecs
import json
import os

from flask import render_template, send_from_directory, request

from CPanel import app
from app.modules.utils.Utils import getINI
from . import main
from ..modules.utils import login_required_

__author__ = 'Jux.Liu'


@main.route('/')
@main.route('/index/')
@login_required_
def index():
    """
打开主页面
    :param: null
    :return: index.html
    """
    # return render_template('index.html')
    return render_template('base.html', language=getINI(section='other', option='lang'))


@main.route('/most3d/')
@login_required_
def most3d():
    """
打开 3DMOST 模型库页面
    :param: null
    :return:
    """
    return render_template('most3d.html')


@main.route('/get_most3d/', methods=['GET', 'POST'])
def get_most3d():
    return render_template('most3d.html')


@main.route('/wizard/')
@login_required_
def wizard():
    """
打开向导页面
    :param: null
    :return:
    """
    return render_template('wizard.html')


@main.route('/get_wizard/', methods=['GET', 'POST'])
def get_wizard():
    return render_template('wizard.html')


@main.route('/app/')
@login_required_
def getapp():
    """
打开 APP 下载页面
    :param: null
    :return: app.html
    """
    return render_template('app.html')


@main.route('/help/<int:id>/')
@login_required_
def help(id):
    """
打开帮助页面
    :param: null
    :return: help.html
    """
    from app import g_p_
    res = None
    with open('{path}{filename}.html'.format(path=g_p_.docPath, filename=id), 'r') as f:
        res = {'help': f.read()}
    return json.dumps(res)


@main.route('/get-help/', methods=['GET', 'POST'])
def get_help():
    if request.method == 'POST':
        dir = 'app/md/'
        filename = request.get_json()['file_name']
        filedir = dir + filename + '.md'
        file = codecs.open(filedir, mode='r', encoding='utf8')
        text = file.read()
        return json.dumps(text if len(text) > 0 else {'code': 30})


@main.route('/favicon.ico/')
def favicon():
    """
站点图标设置
    :param: null
    :return:
    """
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')
