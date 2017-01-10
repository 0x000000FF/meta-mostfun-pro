#!/usr/bin/env python
# coding: utf-8
'''
login 路由定义
'''

from datetime import datetime as dt

from app import g_p_, login_manager, logger
from app.modules.utils.Utils import getINI, modINI
from flask import render_template, redirect, url_for, request, session, jsonify
from flask_login import login_user, current_user, logout_user
from . import user
from .models import User
from ..utils import login_required_

__author__ = 'Jux.Liu'


def remind_maintain():
    """
定期提醒保养
    :return:
    """
    # maintenancetime = getINI(section='maintenance', option='maintenancetime')
    # logger.info('maintenancetime {}'.format(maintenancetime))
    # if maintenancetime > 10:
    #     return True
    # else:
    #     return False
    printedalarm = getINI(section='other', option='printedalarm')
    printedsecs = getINI(section='other', option='printedsecs')
    if int(printedsecs) >= int(printedalarm):
        return True
    else:
        return False


@user.route('/login/', methods=['POST', 'GET'])
def loginPage():
    '''
登录页面
    :param: null
    :return: login.html
    '''
    if current_user.is_authenticated:
        logger.info('auto login')
        return redirect(url_for('main.index'))
    style = 'none'

    if request.method == 'POST':
        id = len(g_p_.LoginList)
        password = request.get_json()['password']
        remember = True if request.get_json()['remember'] == 'y' else False

        if id not in g_p_.LoginList:
            g_p_.LoginList[id] = {'pe_count': 0, 'pe_lasttime': None}

        _su = g_p_.LoginList[id]

        if _su['pe_count'] >= 5:
            lock_delay = (dt.now() - _su['pe_lasttime']).seconds / 60
            if lock_delay < 5:
                # todo: modify the error msg
                logger.warning('login lock')
                return jsonify({'code': 2, 'msg':
                                'please retry after {0} minutes'.format(lock_delay)})

            else:
                logger.warning('login lock retrun to 0')
                _su['pe_count'] = 0

        else:
            u = User(id, password)

            if u.verify_user():
                _su['pe_count'] = 0
                login_user(u, remember=remember)

                res = remind_maintain()
                logger.info('login ok')
                return jsonify({'url': request.args.get('next') or url_for('main.index'),
                                'maintenancetime': res})

            else:
                _su['pe_count'] += 1
                _su['pe_lasttime'] = dt.now()
                logger.warning('login fail {}'.format(_su['pe_count']))
                return jsonify({'code': 35})
    return render_template("login.html", language=getINI(section='other', option='lang'))


@user.route("/logout/", methods=['POST', 'GET'])
@login_required_
def logoutPage():
    """
登出操作
    :param: null
    :return: 重定向到 login.html
    """
    logout_user()
    logger.info('logout')
    session['id'] = None
    session['password'] = None
    return redirect(url_for(".loginPage"))


@login_manager.user_loader
def load_user(user_id):
    """
加载用户的回调函数，接收惟一表示用户的id标识符，如果
能找到用户，则返回用户对象，否则返回None
    :param user_id: 接收到的用户id
    :return: 用户对象
    """
    user = User(user_id)
    if user.id == user_id:
        return user
    else:
        return None


@user.route('/recovery/', methods=['POST'])
@login_required_
def recovery():
    """
    保养完成，重置相关数据
    :return: {"state": "ok/fail"}
    """
    maintenance = request.get_json()['maintenace']
    if maintenance:
        res = modINI(section='other', option="printedsecs", value=0)
        if res:
            return jsonify({"state": "ok"})
    return jsonify({"state": "fail"})
