#!/usr/bin/env python
# coding: utf-8
'''

'''

from flask import Blueprint

from models import SMail

__author__ = 'Jux.Liu'

utils = Blueprint('utils', __name__)
mail = SMail()

from .Utils import login_required_, copyFile, deleteFileFolder
from models import MobileDetector
from . import mail

mobile_detector = MobileDetector()
