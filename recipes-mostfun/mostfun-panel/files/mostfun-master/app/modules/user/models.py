#!/usr/bin/env python
# coding: utf-8
'''
User类
'''
from flask.ext.login import UserMixin

from app.modules.utils.Utils import getINI, modINI

__author__ = 'Jux.Liu'


class User(UserMixin):
    def __init__(self, id, password='mostfun'):
        self.id = id
        self.password = password

    def verify_user(self):
        if getINI('user', 'password') == self.password:
            return True
        else:
            return False
    def changePassword(self, oldPwd, newPwd):
        result = False
        msg = ''
        if oldPwd:
            if self.password != oldPwd:
                pass
            else:
                if len(newPwd):
                     modINI(section='user', option='password', value=newPwd)
                     result = True
                else:
                    pass
        else:
            pass
        return result
