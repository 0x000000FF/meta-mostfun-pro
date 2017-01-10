# -*- coding:utf-8 -*-
from __future__ import division

import os
import re
import shutil
import subprocess
import threading
from time import sleep, time

import Image
import ImageDraw
import ImageFont
import mraa
from configobj import ConfigObj

from app import g_p_
from ..utils.Utils import getINI,modINI
from ..utils import mail
from ... import logger

from evdev import InputDevice
from select import select

# number = 0

# FONT_CN = r'/mostfun/panel/font/HelveticaNeueLTPro-Cn.otf'
# FONT_BDCN = r'/mostfun/panel/font/HelveticaNeueLTPro-BdCn.otf'
# FONT_MDCN = r'/mostfun/panel/font/HelveticaNeueLTPro-MdCn.otf'

FONT_CN_ZH = r'/mostfun/panel/font/SourceHanSansCN-Normal.otf'
FONT_MDCN_ZH = r'/mostfun/panel/font/SourceHanSansCN-Regular.otf'
FONT_BDCN_ZH = r'/mostfun/panel/font/SourceHanSansCN-Medium.otf'
# //font_CN
# FONT_MDCN = r'/mostfun/panel/font/SourceHanSansCN-Medium.otf'

PATH_LOCAL = r'/home/mostfuncp/gcode/'
PATH_SDCARD = r'/media/sdcard/'
PATH_USB = r'/media/usb/'
PATH_PAUSED = r'/home/mostfuncp/paused/'
PATH_INTERRUPTED = r'/home/mostfuncp/interrupted/'
PATH_TMP = r'/home/mostfuncp/tmp/'

# icons
ICON_PATH_PRINT = r'/mostfun/panel/bg/icon/start.bmp'
ICON_PATH_STOP = r'/mostfun/panel/bg/icon/stop.bmp'
ICON_PATH_PAUSE = r'/mostfun/panel/bg/icon/pause.bmp'
BTN_PATH_UP0 = r'/mostfun/panel/bg/icon/up0.bmp'
BTN_PATH_UP1 = r'/mostfun/panel/bg/icon/up1.bmp'
BTN_PATH_DOWN0 = r'/mostfun/panel/bg/icon/down0.bmp'
BTN_PATH_DOWN1 = r'/mostfun/panel/bg/icon/down1.bmp'
BTN_PATH_TEMP_UP0 = r'/mostfun/panel/bg/icon/t_up0.bmp'
BTN_PATH_TEMP_UP1 = r'/mostfun/panel/bg/icon/t_up1.bmp'
BTN_PATH_TEMP_DOWN0 = r'/mostfun/panel/bg/icon/t_down0.bmp'
BTN_PATH_TEMP_DOWN1 = r'/mostfun/panel/bg/icon/t_down1.bmp'

ICON_PATH_ERROR = r'/mostfun/panel/bg/icon/error.bmp'
ICON_PATH_WIFI = r'/mostfun/panel/bg/icon/wifi.bmp'
ICON_PATH_AP = r'/mostfun/panel/bg/icon/ap.bmp'
ICON_PATH_REPAIR = r'/mostfun/panel/bg/icon/repair.bmp'

# imgs
IMG_PATH_ROLLING_BOX0 = r'/mostfun/panel/bg/img/rolling_box0.bmp'
IMG_PATH_ROLLING_BOX1 = r'/mostfun/panel/bg/img/rolling_box1.bmp'
IMG_PATH_FEEDIN = r'/mostfun/panel/bg/img/feedin.bmp'
IMG_PATH_PULLOUT = r'/mostfun/panel/bg/img/pullout.bmp'
IMG_PATH_FEEDIN1 = r'/mostfun/panel/bg/img/feedin1.bmp'
IMG_PATH_PULLOUT1 = r'/mostfun/panel/bg/img/pullout1.bmp'
IMG_PATH_FEEDIN2 = r'/mostfun/panel/bg/img/feedin2.bmp'
IMG_PATH_PULLOUT2 = r'/mostfun/panel/bg/img/pullout2.bmp'
IMG_HEATING1 = r'/mostfun/panel/bg/img/heating1.bmp'
IMG_HEATING2 = r'/mostfun/panel/bg/img/heating2.bmp'
IMG_HEATING3 = r'/mostfun/panel/bg/img/heating3.bmp'
IMG_HEATINGEX1 = r'/mostfun/panel/bg/img/heatingex1.bmp'
IMG_HEATINGEX2 = r'/mostfun/panel/bg/img/heatingex2.bmp'
IMG_HEATINGBED1 = r'/mostfun/panel/bg/img/heatingbed1.bmp'
IMG_HEATINGBED2 = r'/mostfun/panel/bg/img/heatingbed2.bmp'
IMG_LEVELING0 = r'/mostfun/panel/bg/img/leveling0.bmp'
IMG_LEVELING1 = r'/mostfun/panel/bg/img/leveling1.bmp'
IMG_LEVELING2 = r'/mostfun/panel/bg/img/leveling2.bmp'
IMG_LEVELING3 = r'/mostfun/panel/bg/img/leveling3.bmp'
IMG_LEVELING4 = r'/mostfun/panel/bg/img/leveling4.bmp'
IMG_LEVELING5 = r'/mostfun/panel/bg/img/leveling5.bmp'
IMG_LEVELING6 = r'/mostfun/panel/bg/img/leveling6.bmp'
IMG_LEVELING7 = r'/mostfun/panel/bg/img/leveling7.bmp'
IMG_LEVELING8 = r'/mostfun/panel/bg/img/leveling8.bmp'
IMG_LEVELING9 = r'/mostfun/panel/bg/img/leveling9.bmp'
IMG_LEVELING10 = r'/mostfun/panel/bg/img/leveling10.bmp'

IMG_PATH_EX1 = r'/mostfun/panel/bg/img/ex1.bmp'
IMG_PATH_EX2 = r'/mostfun/panel/bg/img/ex2.bmp'
IMG_PATH_EX3 = r'/mostfun/panel/bg/img/ex3.bmp'
IMG_PATH_EX4 = r'/mostfun/panel/bg/img/ex4.bmp'
IMG_PATH_QRwlan1 = r'/mostfun/panel/bg/img/QRwlan1.bmp'
IMG_PATH_QRwlan0 = r'/mostfun/panel/bg/img/QRwlan0.bmp'
# backgrands
PATH_QR_AP = r'/mostfun/panel/bg/bg/back.bmp'
PATH_QR_STA = r'/mostfun/panel/bg/bg/back.bmp'
PATH_LOGO = r'/mostfun/panel/bg/bg/logo.bmp'
PATH_BLACK = r'/mostfun/panel/bg/bg/back.bmp'
PATH_ATTENTION = r'/mostfun/panel/bg/bg/attention.bmp'
PATH_WARNING = r'/mostfun/panel/bg/bg/warning.bmp'
PATH_ERROR = r'/mostfun/panel/bg/bg/error.bmp'
PATH_SETTING = r'/mostfun/panel/bg/bg/setting.bmp'
PATH_UPGRADE = r'/mostfun/panel/bg/bg/upgrading.bmp'
PATH_EXTRUD = r'/mostfun/panel/bg/bg/extrud.bmp'
PATH_TEST = r'/mostfun/panel/bg/bg/test.bmp'
PATH_POEWRDOWN = r'/mostfun/panel/bg/bg/powerdown.bmp'
PATH_REFILLTEST = r'/mostfun/panel/bg/bg/refilltest.bmp'
PATH_SLEEP = r'/mostfun/panel/bg/bg/logo.bmp'
PATH_HEATING = r'/mostfun/panel/bg/bg/heating.bmp'
PATH_LEVELING = r'/mostfun/panel/bg/bg/back.bmp'
PATH_ADJUSTING = r'/mostfun/panel/bg/bg/adjusting.bmp'

PATH_FRAME_BUFFER = r'/tmp/page.bmp'

COLOR_WHIT = 0xFFFFFF
COLOR_BLACK = 0x00
COLOR_DARK_GRAY = 0x666666
COLOR_LIGHT_GRAY = 0xAAAAAA
COLOR_RED = 0x0000FF
COLOR_BLUE = 0xFF0000
COLOR_GREEN = 0x00FF00

BUTTON_H = 34
BUTTON_W = 64

TEXT_LIST_W = 160
TEXT_LIST_TEXT_W = 136


Page_timer = 0

Current_gcode_PATH = ""
Current_page = None
Local_files = []
SDcard_files = []

lang = getINI("other", "lang")
printedsecs = int(getINI("other", "printedsecs"))
printedalarm = int(getINI("other", "printedalarm"))

if lang == 'zh-CN':
    UIconfig = ConfigObj("/mostfun/panel/app/modules/device/ZH.ini", encoding='UTF8')
else:
    UIconfig = ConfigObj("/mostfun/panel/app/modules/device/EN.ini", encoding='UTF8')
    # font_cn16 = ImageFont.truetype(FONT_CN, 16)
    # font_cn18 = ImageFont.truetype(FONT_CN, 18)
    # font_cn20 = ImageFont.truetype(FONT_CN, 20)
    # font_bdcn20 = ImageFont.truetype(FONT_BDCN, 20)
    # font_bdcn30 = ImageFont.truetype(FONT_BDCN, 30)
    # font_mdcn24 = ImageFont.truetype(FONT_MDCN, 24)
    # font_mdcn30 = ImageFont.truetype(FONT_MDCN, 30)
font_cn16 = ImageFont.truetype(FONT_CN_ZH, 16)
font_cn18 = ImageFont.truetype(FONT_CN_ZH, 18)
font_cn20 = ImageFont.truetype(FONT_CN_ZH, 20)

font_bdcn18 = ImageFont.truetype(FONT_BDCN_ZH, 18)
font_bdcn20 = ImageFont.truetype(FONT_BDCN_ZH, 20)
font_bdcn24 = ImageFont.truetype(FONT_BDCN_ZH, 24)
font_bdcn26 = ImageFont.truetype(FONT_BDCN_ZH, 26)
font_bdcn28 = ImageFont.truetype(FONT_BDCN_ZH, 28)
font_bdcn30 = ImageFont.truetype(FONT_BDCN_ZH, 30)

font_mdcn20 = ImageFont.truetype(FONT_MDCN_ZH, 20)
font_mdcn24 = ImageFont.truetype(FONT_MDCN_ZH, 24)
font_mdcn26 = ImageFont.truetype(FONT_MDCN_ZH, 26)
font_mdcn28 = ImageFont.truetype(FONT_MDCN_ZH, 28)
font_mdcn30 = ImageFont.truetype(FONT_MDCN_ZH, 30)

font_mdcn50 = ImageFont.truetype(FONT_MDCN_ZH, 50)
# font_cn16 = ImageFont.truetype(FONT_CN_ZH, 16)
# font_cn18 = ImageFont.truetype(FONT_CN_ZH, 18)
# font_cn20 = ImageFont.truetype(FONT_CN_ZH, 20)
# font_mdcn24 = ImageFont.truetype(FONT_MDCN_ZH, 24)
# font_mdcn30 = ImageFont.truetype(FONT_MDCN_ZH, 30)
# font_bdcn30 = ImageFont.truetype(FONT_BDCN_ZH, 30)

Black_light = bl = mraa.Gpio(21)
LCD_SLEEP_TIMEOUT = 30
sleep_time = time()
Lcd_sleep = False
screen = Image.open(PATH_SLEEP)
screen_draw = ImageDraw.Draw(screen)
p = subprocess.Popen("hostname", shell=True,stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
p.wait()
hostname = p.stdout.readlines()[0]
screen_draw.text((5,5),hostname, COLOR_WHIT, font_cn16)

currentIP = ''

#sdPin = mraa.Gpio(6)
#cmd_check_card_reader_name = "find /sys/devices/pci0000\:00/0000\:00\:11.0/dwc3-host.2/usb1/1-1/1-1.4/1-1.4\:1.0/ -name sd[a-z] | cut -d \/ -f 15"
#cmd_check_USBstorage_name = "find /sys/devices/pci0000\:00/0000\:00\:11.0/dwc3-host.2/usb1/1-1/1-1.3/1-1.3\:1.0/ -name sd[a-z] | cut -d \/ -f 15"
# cmd_get_TFT_PID = '''ps | grep TFT_8340 |  grep -v "grep" | cut -d ' ' -f 3'''
# cmd_get_TFT_PID = "ps | grep TFT_8340 | grep -v grep | awk '{print$1}'"
SDcard = False
USBstorage = False
TFT_PID = 0

class base_ele(object):
    def  __init__(self,location,size,container=None,backgrand=None,isenable=True,isvisiable=True,isselected=0,handle=None,handleargs=None):
        self.location = location
        self.size = size
        self.container = container
        self.backgrand = backgrand
        self.isenable = isenable
        self.isvisiable = isvisiable
        self.isselected = isselected
        self.handle = handle
        self.handleargs = handleargs

    def click(self):
        if self.isenable:
            if self.handleargs == None:
                self.handle()
            else:
                self.handle(self.handleargs)
        else:
            pass

    def left_click(self):
        global Current_page
        Current_page.last_element()

    def right_click(self):
        global Current_page
        Current_page.next_element()

    def disable(self):
        self.isenable = False

    def enable(self):
        self.isenable = True

    def visiable(self):
        self.isvisiable = True
        self.isselected = 0

    def unvisiable(self):
        self.isvisiable = False
        if self.isselected == 1:
            self.right_click()

    def draw(self):
        pass

class rolling_box(base_ele):
    def __init__(self, location,value_range, step,icons, handle, handleargs=None):
        base_ele.__init__(self,location=location,size=size,handle=handle,handleargs=handleargs)
        for icon in icons :
            self.icons.append(Image.open(icon))
        self.active = False
        self.value_range = [0,0]
        self.value = 0
        self.step = 1
        self.images = list()
        self.images_location = ()
        self.text_location = (self.location[0]+5,self.location[1]+3)

    def add_images(self,image_path,location):
        for path in image_path:
            self.images.append(Image.open(path))
        self.images_location = location

    def click(self):
        self.active = not self.active

    def left_click(self):
        if self.active:
            self.value -= self.step
        else:
            base_ele.left_click(self)

    def right_click(self):
        if self.active:
            self.value += self.step
        else:
            base_ele.right_click(self)

    def draw(self):
        if self.isselected:
            self.backgrand.paste(self.icons[0], self.location)
            self.container.text(self.text_location, self.value, COLOR_WHIT, font_cn16)
            if len(self.images) > 1:
                self.backgrand.paste(self.images[0], self.images_location)
        else:
            self.backgrand.paste(self.icons[1], self.location)
            self.container.text(self.text_location, self.value, COLOR_WHIT, font_cn16)
            if len(self.images) > 1:
                self.backgrand.paste(self.images[1], self.images_location)

class button(base_ele):
    def __init__(self, location,size, text, handle, handleargs=None):
        base_ele.__init__(self,location=location,size=size,handle=handle,handleargs=handleargs)
        self.text = text
        self.warning = False
        self.location2 = (self.location[0]+self.size[1],self.location[1]+self.size[0])

    def set_warning(self, warning=True):
        self.warning = warning

    def draw(self):
        textsize = self.container.textsize(self.text, font_bdcn30)
        textlocation = ((self.size[1]-textsize[0])/2+self.location[0],(self.size[0]-textsize[1])/2+self.location[1]+8)
        if self.isvisiable == True:
            if self.isenable == True:
                if self.selected == 0:
                    self.container.rectangle((self.location, self.location2), COLOR_BLACK)
                    self.container.text(textlocation, self.text, COLOR_WHIT, font_bdcn30)
                if self.selected == 1:
                    if self.warning:
                        self.container.rectangle((self.location, self.location2), COLOR_RED)
                        self.container.text(textlocation, self.text, COLOR_WHIT, font_bdcn30)
                    else:
                        self.container.rectangle((self.location, self.location2), COLOR_WHIT)
                        self.container.text(textlocation, self.text, COLOR_BLACK, font_bdcn30)
            elif self.isenable == False:
                if self.selected == 1:
                    self.container.rectangle((self.location, self.location2), COLOR_LIGHT_GRAY)
                    self.container.text(textlocation, self.text, COLOR_DARK_GRAY, font_bdcn30)
                if self.selected == 0:
                    self.container.rectangle((self.location, self.location2), COLOR_BLACK)
                    self.container.text(textlocation, self.text, COLOR_DARK_GRAY, font_bdcn30)


class button_img(base_ele):
    def __init__(self, location, imgpath, handle, args=None):
        base_ele.__init__(self,location=location,size=(0,0),handle=handle,handleargs=args)
        self.img = list()
        # 0:not selected 1:selected 2:disabled
        for path in imgpath:
            self.img.append(Image.open(path))
        self.warning = False
        # self.location2 = (self.location[0]+self.img[0].size[0],self.location[1]+self.img[0].size[1])
        self.images = list()
        self.images_location = ()
        
    def add_images(self,image_path,location):
        for path in image_path:
            self.images.append(Image.open(path))
        self.images_location = location

    def set_warning(self, warning=True):
        self.warning = warning

    def draw(self):
        if self.isenable:
            if self.selected == 0:
                self.backgrand.paste(self.img[0], self.location)
                if len(self.images) > 1:
                    self.backgrand.paste(self.images[0], self.images_location)
                
            if self.selected == 1:
                self.backgrand.paste(self.img[1], self.location)
                if len(self.images) > 1:
                    self.backgrand.paste(self.images[1], self.images_location)
        else:
            self.backgrand.paste(self.img[-1], self.location)


class menu(object):
    def __init__(self, name, items):
        self.name = name
        self.items = list()
        global UIconfig
        section = UIconfig[name]
        state = section['state']
        name = section.values()
        for i in range(0, len(items)):
            templist = list()
            templist.append(name[i])
            templist.append(items[i])
            templist.append(state[i])
            self.items.append(templist)

        self.current_item = self.items[0]
        self.container = None
        self.backgrand = None
        self.selected = 0

    def click(self):
        jump2page(self.current_item[1])

    def left_click(self):
        while True:
            self.current_item = self.items[self.items.index(self.current_item) - 1]
            if self.current_item[2] == "e":
                return

    def right_click(self):
        while True:
            if self.current_item == self.items[-1]:
                self.current_item = self.items[0]
            else:
                self.current_item = self.items[self.items.index(self.current_item) + 1]
            if self.current_item[2] == "e":
                return

    def disable_item(self, item_num):
        self.items[item_num][2] = "d"

    def enable_item(self, item_num):
        self.items[item_num][2] = "e"

    def hidden_item(self, item_num):
        self.items[item_num][2] = "h"

    # def drop_item(self,item_num):
    #     if self.current_item == self.items[item_num]:
    #         pass
    #     self.items.remove(item_num)

    # def additem(self,index,item):
    #     self.items.insert(index,item)

    def draw(self):
        rectangle = 30
        self.container.rectangle((0, 16, 219, 175), COLOR_BLACK)
        if not self.current_item[2] == "e":
            self.right_click()
        for item in self.items:
            if item[2] == "h":
                # self.right_click()
                continue
            if self.current_item == item:
                self.container.rectangle((0, rectangle - 2, 205, rectangle + 30), COLOR_WHIT)
                self.container.text((20, rectangle + 2), item[0], COLOR_BLACK, font_mdcn28)
                rectangle += 27
            else:
                if item[2] == "e":
                    self.container.text((20, rectangle + 7), item[0], COLOR_WHIT, font_cn18)
                elif item[2] == "d":
                    self.container.text((20, rectangle + 7), item[0], COLOR_DARK_GRAY, font_cn18)
                rectangle += 27


class file_list(object):
    def __init__(self, name, dirpath):
        self.name = name
        self.path = dirpath
        self.files = []
        self.refresh()
        self.current = 0
        self.offset = 0
        self.window_size = 5
        self.container = None
        self.backgrand = None
        self.selected = 0
        self.rolloffset = 0
        self.counter = 0

    def click(self):
        global Current_gcode_PATH
        if not len(self.files) == 0:
            Current_gcode_PATH = self.path + self.files[self.current]
            comfirming(self.files[self.current])
        else:
            jump2page(p_main_menu)
        self.rolloffset = 0
        self.counter = 0

    def left_click(self):
        if self.current > 0:
            self.current -= 1
        elif self.current == 0:
            self.current = len(self.files) - 1
        if self.current < self.offset:
            self.offset = self.current
        elif self.current > self.offset + (self.window_size-1):
            self.offset = self.current - (self.window_size-1)
        self.rolloffset = 0
        self.counter = 0

    def right_click(self):
        if self.current < len(self.files) - 1:
            self.current += 1
        elif self.current == len(self.files) - 1:
            self.current = 0
        if self.current < self.offset:
            self.offset = self.current
        elif self.current > self.offset + (self.window_size-1):
            self.offset = self.current - (self.window_size-1)
        self.rolloffset = 0
        self.counter = 0

    def refresh(self):
        if not os.path.exists(self.path):
            self.files = []

    def _compare(self,x, y):
        stat_x = os.stat(self.path + "/" + x)
        stat_y = os.stat(self.path + "/" + y)
        if stat_x.st_ctime > stat_y.st_ctime:
            return -1
        elif stat_x.st_ctime < stat_y.st_ctime:
            return 1
        else:
            return 0

    def draw(self):
        if os.path.exists(self.path):
            self.files = os.listdir(self.path)
            self.files.sort(self._compare)
            list_temp = list()
            for f in self.files:
                # print '---------'
                if f.endswith('.gcode'):
                    # try:
                    #     f = f.decode('utf-8')
                    # except Exception as e:
                    #     logger.error('file name decode failed')
                    # # f = f[0:-6]
                    list_temp.append(f)
            self.files = list_temp

            self.container.rectangle((0, 34, 190, 175), COLOR_BLACK)
            self.container.line(((0, 30), (TEXT_LIST_W, 30)), fill=COLOR_WHIT, width=2)
            if len(self.files) == 0:
                self.container.text((50, 45), UIconfig["mesg"]["empty"], COLOR_WHIT, font_cn18)
                return
            rectangle = 34
            rang = len(self.files)
            if rang>self.window_size:
                rang = self.window_size
            for i in range(self.offset,self.offset+rang):
                item = self.files[i].decode()
                item = item[0:-6]
                if self.current == i:
                    # draw selected item  .decode('utf-8').decode('utf-8')
                    self.container.rectangle((0, rectangle, TEXT_LIST_W, rectangle + 28), COLOR_WHIT)
                    if self.container.textsize(item, font_bdcn24)[0] <= TEXT_LIST_TEXT_W:
                        # short enough,no rolling
                        self.container.text((20, rectangle + 3), item, COLOR_BLACK, font_mdcn24)
                    else:
                        # long enough,rolling
                        img_w = self.container.textsize(item, font_bdcn24)[0] + TEXT_LIST_TEXT_W
                        img_tmp = Image.new("RGB", (img_w, 28), "white")
                        draw_tmp = ImageDraw.Draw(img_tmp)
                        draw_tmp.text((3, 3), item, COLOR_BLACK, font_mdcn24)
                        w = img_tmp.size[0]
                        box = (self.rolloffset, 0, self.rolloffset + TEXT_LIST_TEXT_W, 28)
                        disp = img_tmp.crop(box)

                        self.backgrand.paste(disp, (20, rectangle, 20 + TEXT_LIST_TEXT_W, rectangle + 28))
                        # self.container.text((20-self.rolloffset,rectangle+3),item,COLOR_BLACK,font_mdcn24)

                        if self.rolloffset >= img_w - TEXT_LIST_TEXT_W:
                            self.rolloffset = 0
                            self.counter = 0

                        self.counter += 1
                        if self.counter > 10:
                            self.rolloffset += 2

                    rectangle += 28

                else:
                    # pass
                    width = self.container.textsize(item, font_cn16)[0]
                    # draw unselected item
                    if width <= TEXT_LIST_TEXT_W:
                        self.container.text((20, rectangle + 3), item, COLOR_WHIT, font_cn16)
                    else:
                        self.container.text((20, rectangle + 3),
                                            item[:int(len(item) * (TEXT_LIST_TEXT_W / width)) - 2] + u"…", COLOR_WHIT,
                                            font_cn16)
                    rectangle += 24

            # draw sidebar
            if len(self.files) - 1 == 0:
                slider = 30
            else:
                slider = self.current / (len(self.files) - 1) * 102 + 30

            self.container.rectangle((160, 0, 219, 175), COLOR_BLACK)
            self.container.line(((200, 30), (200, 146)), fill=COLOR_WHIT, width=2)
            self.container.line(((200, slider), (200, slider + 14)), fill=COLOR_WHIT, width=8)


class printing(object):
    def __init__(self, name, printer):
        self.container = None
        self.backgrand = None
        self.selected = -1
        self.layers = 0
        self.current_layer = 0
        self.layer_offset = 0
        self.percent = 0
        self.E_temp = 0.0
        self.B_temp = 0.0
        self.E_target_temp = 0.0
        self.E_target_temp = 0.0
        self.time = "00:00:00"
        self.state = "--"
        self.icon_start = Image.open(ICON_PATH_PRINT, 'r')
        self.icon_stop = Image.open(ICON_PATH_STOP, 'r')
        self.icon_pause = Image.open(ICON_PATH_PAUSE, 'r')
        self.printer = printer
        self.file_name = Current_gcode_PATH.split(r'/')[-1]

    def refresh_printer_state(self):
        global Current_gcode_PATH
        if not self.file_name == Current_gcode_PATH.split(r'/')[-1]:
            # print Current_gcode_PATH.split(r'/')[-1]
            self.file_name = Current_gcode_PATH.split(r'/')[-1]
            print_name_rolling.set_text(self.file_name)
        Current_gcode_PATH = self.printer.get_currentfile()
        self.time = self.printer.get_times()
        self.layer_offset = self.printer._g.layer_offset
        self.current_layer = self.printer._g.layerNum - self.layer_offset
        self.layers = self.printer._g.layerCount - self.layer_offset
        self.percent = self.printer.get_percent()
        self.E_temp = self.printer.get_extruderTemp()
        self.B_temp = self.printer.get_bedTemp()
        self.E_target_temp = self.printer.get_extruderTargetTemp()
        self.B_target_temp = self.printer.get_bedTargetTemp()
        self.state = self.printer.get_state()

    def reset_state(self):
        self.layers = 0
        self.current_layer = 0
        self.percent = 0
        self.time = "00:00:00"

    def click(self):
        if self.state == "printing" or self.state == "pause":
            jump2page(p_printing_ctl_menu)
        else:
            jump2page(p_main_menu)

    def left_click(self):
        if self.state == "printing" or self.state == "pause":
            pass
        else:
            jump2page(p_main_menu)

    def right_click(self):
        self.left_click()

    def draw(self):
        self.container.rectangle((0, 32, 219, 175), COLOR_BLACK)

        if self.state == "printing":
            self.backgrand.paste(self.icon_start, (8, 115, 40, 147))

        elif self.state == "pause":
            self.backgrand.paste(self.icon_pause, (8, 115, 40, 147))

        self.container.text((10, 48), UIconfig["mesg"]["layers"] + str(self.current_layer) + '/' + str(self.layers),
                            COLOR_WHIT,
                            font_cn18)
        # self.container.text((10,67),"E_Temp:"+str(self.E_temp)+r'/'+str(self.E_target_temp)+'C',COLOR_WHIT,font_cn18)
        # self.container.text((10,89),"B_Temp:"+str(self.B_temp)+r'/'+str(self.B_target_temp)+'C',COLOR_WHIT,font_cn18)
        self.container.text((10, 75), UIconfig["mesg"]["complete"] + '%0.2f' % (self.percent) + '%', COLOR_WHIT,
                            font_cn18)

        # draw time
        self.container.text((210 - self.container.textsize(str(self.time), font_mdcn50)[0], 105), str(self.time),
                            COLOR_WHIT, font_mdcn50)
        # draw process bar
        self.container.line(((10, 155), (210, 155)), fill=COLOR_WHIT, width=1)
        self.container.line(((10, 166), (210, 166)), fill=COLOR_WHIT, width=1)
        self.container.line(((10, 155), (10, 166)), fill=COLOR_WHIT, width=1)
        self.container.line(((210, 155), (210, 166)), fill=COLOR_WHIT, width=1)
        # draw process bar process
        if self.percent >= 0:
            self.container.line(((12, 161), (int(12 + 196.0 * (self.percent / 100.0)), 161)), fill=COLOR_WHIT, width=8)


class static_p(object):
    def __init__(self):
        self.selected = -1

    def click(self):
        jump2page(Last_page)

    def left_click(self):
        jump2page(Last_page)

    def right_click(self):
        jump2page(Last_page)

    def draw(self):
        pass


class textbox(object):
    def __init__(self, position, textshow, style="middle", fontb=font_cn18, fonts=font_cn16):
        if position == "center":
            self.X = 4
            self.Y = 50
            self.XX = 215
            self.YY = 106
        else:
            self.X = position[0]
            self.Y = position[1]
            self.XX = position[2]
            self.YY = position[3]
        self.style = style
        #self.textstr = textshow
        self.textstr = textshow.decode('utf-8')
        self.selected = -1
        self.container = None
        self.backgrand = None
        self.fontb = fontb
        self.fonts = fonts
        self.font = fontb
        self.cursor = [0, 0]
        self.char_H = 0
        self.char_W = 0

    def set_text(self, text):
        self.textstr = text.decode('utf-8')

    def type_a_char(self, char):
        width = self.container.textsize(char, self.font)[0]
        height = self.container.textsize(char, self.font)[1]
        if height + self.cursor[1] > self.YY - self.Y:
            return
        if char == '\n':
            self.cursor[0] = 0
            self.cursor[1] += height
            return
        if (width + self.cursor[0] > self.XX - self.X):
            self.cursor[0] = 0
            self.cursor[1] += height

        self.container.text((self.cursor[0] + self.X, self.cursor[1] + self.Y), char, COLOR_WHIT, self.font)
        self.cursor[0] += width

    def draw(self):
        size = self.container.textsize(self.textstr, self.font)
        if size[0] * size[1] > (self.XX - self.X) * (self.YY - self.Y):
            self.font = self.fonts

        self.container.rectangle((self.X, self.Y, self.XX, self.YY), COLOR_BLACK)
        if (size[0] <= self.XX - self.X) and not '\n' in self.textstr:
            if self.style == "middle":
                self.container.text((self.X + ((self.XX - self.X - size[0]) / 2), self.Y-1),
                                    self.textstr, COLOR_WHIT, self.font)
            elif self.style == "left":
                self.container.text((self.X, self.Y-1), self.textstr, COLOR_WHIT, self.font)
        else:
            # self.cursor[1] = self.YY-self.Y-(size[1]*int(size[0]/(self.XX-self.X)))/2
            for c in self.textstr:
                # print c.encode()
                self.type_a_char(c)
            self.cursor = [0, 0]


class timer_show(object):
    def __init__(self, position, count, font=font_cn20):  # only Y coordinate is needed
        self.position = position
        self.counter = count
        self.selected = -1
        self.container = None
        self.backgrand = None
        self.font = font

    def draw(self):
        current_T = self.counter - int(time() - Page_timer)
        size = self.container.textsize(str(current_T) + "s", self.font)
        self.container.rectangle(
            (self.position[0], self.position[1], self.position[0] + size[0] + 12, self.position[1] + size[1] - 6),
            COLOR_BLACK)
        self.container.text(self.position, str(current_T) + "s", COLOR_WHIT, self.font)


class rolling_text(object):
    def pre_draw(self):
        self.image = Image.new("RGB", (100, 100), "black")
        self.tempdraw = ImageDraw.Draw(self.image)
        self.img_size = self.tempdraw.textsize(self.textstr, self.font)
        self.image = self.image.resize(self.img_size)
        self.tempdraw = ImageDraw.Draw(self.image)
        self.tempdraw.text((0, 3), self.textstr, COLOR_WHIT, self.font)
        self.box = None
        self.disp = None

    def __init__(self, position_Y, textshow, font=font_mdcn24, style='l'):  # only Y coordinate is needed
        self.position = position_Y
        self.textstr = textshow.decode('utf-8')
        self.selected = -1
        self.container = None
        self.backgrand = None
        self.font = font
        self.cursor = [0, 0]
        self.rolloffset = 0
        self.style = style
        self.pre_draw()
        self.speed = 3
        self.dirty = True

    def set_text(self, text):
        self.textstr = text.decode('utf-8')
        self.pre_draw()
        self.dirty = True

    def draw(self):
        if self.dirty == True:
            if self.img_size[0] <= 220:
                if self.style == 'm':
                    self.backgrand.paste(self.image, (
                    (220 - self.img_size[0]) / 2, self.position, (220 - self.img_size[0]) / 2 + self.img_size[0],
                    self.position + self.img_size[1]))
                elif self.style == 'l':
                    self.backgrand.paste(self.image,
                                         (0, self.position, self.img_size[0], self.position + self.img_size[1]))
                elif self.style == 'r':
                    self.backgrand.paste(self.image,
                                         (220 - self.img_size[0], self.position, 220, self.position + self.img_size[1]))
                self.dirty = False
            else:
                # long enough,rolling

                self.box = (self.rolloffset, 0, self.rolloffset + 220, self.img_size[1])
                self.disp = self.image.crop(self.box)

                self.backgrand.paste(self.disp, (0, self.position, 220, self.position + self.img_size[1]))
                if self.rolloffset >= self.img_size[0]:
                    self.rolloffset = 0

                self.rolloffset += self.speed
                self.dirty = True


class image(object):
    def __init__(self, X, Y, imgpath, times=-1):
        self.X = X
        self.Y = Y
        self.img = list()
        for path in imgpath:
            self.img.append(Image.open(path))
        self.selected = -1
        self.container = None
        self.backgrand = None
        self.xx = self.X + self.img[0].size[0]
        self.yy = self.Y + self.img[0].size[1]
        self.frame = 0
        self.times = times
        self.speed = 5

    def play(self, times):
        self.times = times * len(self.img) * self.speed

    def draw(self):
        if self.times == 0:
            self.backgrand.paste(self.img[0], (self.X, self.Y, self.xx, self.yy))
        else:
            if self.frame == len(self.img) * self.speed:
                self.frame = 0
            self.container.rectangle((self.X, self.Y, self.xx, self.yy), COLOR_BLACK)
            self.backgrand.paste(self.img[int(self.frame / self.speed)], (self.X, self.Y, self.xx, self.yy))
            self.frame += 1
            if self.times > 0:
                self.times -= 1


class process_bar(object):
    def __init__(self, (X, Y), (XX, YY), color=COLOR_BLACK):
        self.start = (X, Y)
        self.end = (XX, YY)
        self.persent = 0.0
        self.selected = -1
        self.container = None
        self.backgrand = None
        self.color = color
        self.dirty = True

    def set_persent(self, persent):
        self.persent = persent
        self.dirty = True

    def draw(self):
        if self.dirty == True:
            # print self.persent
            self.container.line((self.start, self.end), fill=COLOR_BLACK, width=5)
            endx = int((self.end[0] - self.start[0]) * self.persent + self.start[0])
            endy = int((self.end[1] - self.start[1]) * self.persent + self.start[1])

            self.container.line((self.start, (endx, endy)), fill=self.color, width=5)
            self.dirty = False


class shap_line(object):
    def __init__(self, location, color=COLOR_BLACK,width=5):
        self.location = location#X1,Y1,X2,Y2
        self.width = width
        self.selected = -1
        self.container = None
        self.backgrand = None
        self.color = color
        self.dirty = True
        self.offset = [0,0]#X,Y 
        self.range = [0,0,0,0]#X+,X-,Y+,Y-

    def set_range(self,ran):
        self.range = ran

    def set_offset(self, offset):
        if self.offset[0]+offset[0]>=self.range[0] and self.offset[0]+offset[0]<=self.range[1] and \
            self.offset[1]+offset[1]>=self.range[2] and self.offset[1]+offset[1]<=self.range[3] :

            self.container.line([self.location[0] + self.offset[0],self.location[1] + 
                    self.offset[1],self.location[2] + self.offset[0],self.location[3] + 
                    self.offset[1]],fill=COLOR_BLACK, width=self.width)
            self.offset[0] += offset[0]
            self.offset[1] += offset[1]
            self.dirty = True

    def draw(self):
        if self.dirty == True:
        # print self.persent
            if self.offset[0]==self.range[0] or self.offset[0]==self.range[1] or \
                self.offset[1]==self.range[2] or self.offset[1]==self.range[3]:
                color = COLOR_RED
            else:
                color = self.color
            self.container.line([self.location[0] + self.offset[0],self.location[1] + 
                self.offset[1],self.location[2] + self.offset[0],self.location[3] + 
                self.offset[1]],fill=color, width=self.width)
            self.dirty = False

class base_show(object):
    def __init__(self,location,size):
        self.location = location#X1,Y1,X2,Y2
        self.size = size
        self.container = None
        self.backgrand = None
        self.selected = -1
        self.dirty = 1

class status_bar(base_show):
    def __init__(self,location=(0,0),size=(220,16)):
        base_show.__init__(self,location=(0,0),size=(220,16))
        self.size = size
        self.location = location
        self.location1 = (self.location[0]+self.size[0],self.location[1]+self.size[1])
        self.container = None
        self.backgrand = None
        self.selected = -1
        self.allstatus = ('error','wifi','ap','repair')
        self.status = []
        self.dirty = 1
        self.imgs = {'error':Image.open(ICON_PATH_ERROR),
            'wifi':Image.open(ICON_PATH_WIFI),
            'ap':Image.open(ICON_PATH_AP),
            'repair':Image.open(ICON_PATH_REPAIR)}

    def add_status(self,status):
        if status in self.allstatus:
            if not status in self.status:
                self.status.append(status)
                self.dirty = 1

    def del_status(self,status):
        if status in self.status:
            self.status.remove(status)
            self.dirty = 1

    def draw(self):
        if self.dirty:
            self.container.rectangle((self.location,self.location1), COLOR_BLACK)
            position = 203
            for status in self.status:
                self.backgrand.paste(self.imgs[status],(position,0))
                position -= 20
            self.dirty = 0

class page(object):
    def __init__(self, backgrand_path, owner=("ready",), enablehoming=True):
        self.backgrand = Image.open(backgrand_path)
        self.container = ImageDraw.Draw(self.backgrand)
        self.elements = []
        self.shows = []
        self.current_element = None
        self.dirty = True
        self.owner = owner
        self.timeout = 0
        self.handle = None
        self.handleargs = None
        self.action = None
        self.actionargs = None
        self.isdisable = False
        self.autojump = None
        self.enable_autojump = False
        self.enable_homing = enablehoming

    def page_enable(self):
        self.isdisable = False

    def page_disable(self):
        self.isdisable = True

    def set_action(self, action, args=None):
        self.action = action
        self.actionargs = args

    def set_timeout(self, timeout, handle, args=None):
        self.timeout = timeout
        self.handle = handle
        self.handleargs = args

    def add_ele(self, ele):
        self.elements.append(ele)
        ele.container = self.container
        ele.backgrand = self.backgrand
        self.current_element = self.elements[-1]

    def add_show(self, show):
        self.shows.append(show)
        show.container = self.container
        show.backgrand = self.backgrand

    def set_auto_jump(self, page):
        self.autojump = page

    def enable_jump(self):
        self.enable_autojump = True

    def disable_jump(self):
        self.enable_autojump = False

    def draw_page(self):
        pass

    def flush_page(self):
        global Page_timer
        if self.isdisable == True:
            jump2page(p_home)
        else:
            if not self.timeout == 0:
                if time() - Page_timer > self.timeout:
                    if not self.handleargs == None:
                        self.handle(self.handleargs)
                    else:
                        self.handle()

            for ele in self.elements:
                if ele == self.current_element:
                    ele.selected = 1
                else:
                    ele.selected = 0
                ele.draw()
            for show in self.shows:
                show.draw()

            self.backgrand.save(PATH_FRAME_BUFFER)

    def last_element(self):
        #TODO, attention ,dead loop probably when set all ele to unvisiable
        while True:
            self.current_element = self.elements[self.elements.index(self.current_element) - 1]
            if self.current_element.isvisiable == True:
                break

    def next_element(self):
        #TODO, attention ,dead loop probably when set all ele to unvisiable
        while True:
            if self.current_element == self.elements[-1]:
                self.current_element = self.elements[0]
            else:
                self.current_element = self.elements[self.elements.index(self.current_element) + 1]
            if self.current_element.isvisiable == True:
                break

    def click(self,key):
        global Page_timer
        Page_timer = time()
        if key == '0':
            try:
                self.current_element.click()
                # Current_page.dirty = True
                print '0'
            except Exception as e:
                pass
        elif key == '1':
            if self.enable_homing == True:
                jump2page(p_home)
                print '1'
            # Current_page.dirty = True

        elif key == '<':
            try:
                self.current_element.left_click()
                # Current_page.dirty = True
            except:
                pass

        elif key == '>':
            try:
                self.current_element.right_click()
                # Current_page.dirty = True
            except:
                pass

def set_language(language):
    global lang
    if language == "en":
        if not lang == "en-US":
            modINI("other","lang", "en-US")
        else:
            return
    elif language == "ch":
        if not lang == "zh-CN":
            modINI("other","lang", "zh-CN")
        else:
            return
    else :
        return
    waiting(UIconfig["mesg"]["wait"])
    sleep(1)
    subprocess.call('systemctl restart mostfun_panel', shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

def black_light(state):
    if state == "on":
        Black_light.write(1)
    elif state == "off":
        Black_light.write(0)


def begin_printing(gcode=None):
    waiting(UIconfig["mesg"]["load"])
    if gcode == None:
        global Current_gcode_PATH
        gcode = Current_gcode_PATH
    if g_p_.mostfun.beginTask(gcode) == False:
        warning(UIconfig["mesg"]["invalid"])
        sleep(3)
        cancel_printing()
        return
    p_home = p_printing
    # print gcode
    p_heating.enable_jump()
    jump2page(p_heating)


def cancel_printing():
    waiting(UIconfig["mesg"]["wait"])
    g_p_.mostfun.cancelTask()
    p_home = p_main_menu
    jump2page(p_home)


def pause_printing():
    g_p_.mostfun.pauseTask()
    # menu_printing_ctl.hidden_item(0)
    # menu_printing_ctl.enable_item(1)
    jump2page(p_home)


def resume_printing():
    g_p_.mostfun.resumeTask()
    # menu_printing_ctl.hidden_item(1)
    # menu_printing_ctl.enable_item(0)
    jump2page(p_home)


def save_printing(powerdown=False):
    waiting(UIconfig["mesg"]["wait"])
    g_p_.mostfun.stop_saveTask(powerdown)
    if powerdown == False:
        p_home = p_main_menu
        jump2page(p_home)


def jump2page(page):
    global Current_page
    global Last_page
    global Page_timer
    Page_timer = time()

    if page == p_printing_ctl_menu:
        if g_p_.mostfun.get_state() == 'pause':
            menu_printing_ctl.enable_item(-1)
            menu_printing_ctl.hidden_item(0)
            menu_printing_ctl.enable_item(1)
        else:
            menu_printing_ctl.disable_item(-1)
            menu_printing_ctl.hidden_item(1)
            menu_printing_ctl.enable_item(0)

    elif page == p_refill:
        g_p_.mostfun.send_command(["G28","G1 F3600 X110 Y120"])
        if g_p_.mostfun.get_extruderTargetTemp() < 210:
            g_p_.mostfun.send_command(["M104 S210.000000"])
    # elif page == p_connection_menu:
    #     waiting(UIconfig["mesg"]["checkwifi"])
    #     check_wifi("wlan0", 1)
    #     check_wifi("ra0", 0)
    elif page == p_continue:
        file_name_rolling.set_text(Current_gcode_PATH.split(r'/')[-1])
    elif page == p_auto_leveling:
        Btn_adjusting.disable()
    if len(page.elements) >= 1:
        page.current_element = page.elements[-1]
    Last_page = Current_page
    Current_page = page


def jumpback():
    global Last_page
    jump2page(Last_page)


def extrud():
    # extrud test gcode
    # M109 S100.000000
    # G91
    # G1 F1200 E10
    # G90
    Img_ex_test.play(8)
    g_p_.mostfun.send_command(["G91", "G1 F200 E20", "G90"])


def Z_up():
    img_bord.set_offset([0,-1])
    g_p_.mostfun.send_command(["G91", "G1 F200 Z-0.1", "G90"])


def Z_down():
    img_bord.set_offset([0,1])
    g_p_.mostfun.send_command(["G91", "G1 F200 Z0.1", "G90"])


def ex_temper_up():
    print g_p_.mostfun.extemper_offset
    if g_p_.mostfun.extemper_offset < 15:
        g_p_.mostfun.extemper_offset += 3
        command = "M104 S" + str(g_p_.mostfun.get_extruderTargetTemp() + 3)
        print command
        g_p_.mostfun.send_command([command])
    print "done"

def ex_temper_down():
    if g_p_.mostfun.extemper_offset > -15:
        g_p_.mostfun.extemper_offset -= 3
        command = "M104 S" + str(g_p_.mostfun.get_extruderTargetTemp() - 3)
        g_p_.mostfun.send_command([command])

def bed_temper_up():
    if g_p_.mostfun._bedTemp < 120:
        g_p_.mostfun.bedtemper_offset += 10
        command = "M140 S" + str(g_p_.mostfun.get_bedTargetTemp() + 10)
        g_p_.mostfun.send_command([command])

def bed_temper_down():
    if g_p_.mostfun._bedTemp > -1:
        g_p_.mostfun.bedtemper_offset -= 10
        command = "M140 S" + str(g_p_.mostfun.get_bedTargetTemp() - 10)
        g_p_.mostfun.send_command([command])

def level_start():
    # g_p_.mostfun.send_command(["G35"])
    g_p_.mostfun.auto_leveling()
    Btn_check_start.text = UIconfig["button"]["OK"]
    Btn_check_start.handle = level_fihish
    Img_leveling.play(-1)
    Btn_check_start.disable()
    Btn_adjusting.disable()

def level_fihish():
    g_p_.mostfun.send_command(["G28","G34"])
    jump2page(p_home)
    Btn_check_start.text = UIconfig["button"]["start"]
    Btn_check_start.handle = level_start
    Btn_adjusting.disable()

def level_hand_check_apply():
    g_p_.mostfun.send_command(["G35"])
    level_fihish()
    waiting(UIconfig["mesg"]["wait"])
    sleep(3)
    jump2page(p_home)
    #level_done()

def level_hand_check_cancel():
    # g_p_.mostfun.send_command(["G28"])
    # jump2page(p_home)
    level_fihish()

def level_done():
    g_p_.mostfun.reset()
    jump2page(p_home)


def waiting(text):
    # print "wait"
    p_waiting.shows[0].textstr = text
    jump2page(p_waiting)


def warning(text):
    p_warning.shows[0].textstr = text
    jump2page(p_warning)

def error(text):
    p_error.shows[0].textstr = text
    jump2page(p_error)

def comfirming(text):
    comfirm_msg.set_text(text)
    jump2page(p_confirm)


def check_interrupt():
    interrupted_file = os.listdir(PATH_INTERRUPTED)
    if len(interrupted_file) == 0:
        return False
    file_name_rolling.set_text(interrupted_file[0])
    global Current_gcode_PATH
    Current_gcode_PATH = PATH_INTERRUPTED + interrupted_file[0]
    tmp_files = os.listdir(PATH_TMP)
    for f in tmp_files:
        os.remove(PATH_TMP + f)
    return True


def save_interrupt():
    waiting(UIconfig["mesg"]["wait"])
    files = os.listdir(PATH_INTERRUPTED)
    for f in files:
        shutil.move(PATH_INTERRUPTED + f, PATH_PAUSED)
    jump2page(p_main_menu)


def skip_interrupt():
    waiting(UIconfig["mesg"]["wait"])
    files = os.listdir(PATH_INTERRUPTED)
    for f in files:
        os.remove(PATH_INTERRUPTED + f)
    jump2page(p_main_menu)


def continue_interrupt():
    global Current_gcode_PATH
    files = os.listdir(PATH_INTERRUPTED)
    for f in files:
        shutil.move(PATH_INTERRUPTED + f, PATH_TMP)
    Current_gcode_PATH = PATH_TMP + files[0]
    begin_printing()


def back2printing():
    p_heating.disable_jump()
    jump2page(p_home)


def check_SD():
    SDcard = os.path.exists(PATH_SDCARD)
    USBstorage = os.path.exists(PATH_USB)
    usb_files.refresh()
    sdcard_files.refresh()

    if SDcard == False and USBstorage == False:
        main_menu.disable_item(-1)
        p_files_menu.page_disable()
    else:
        main_menu.enable_item(-1)
        p_files_menu.page_enable()

    if SDcard == False:
        menu_files.disable_item(0)
        p_files_sdcard.page_disable()
    else:
        menu_files.enable_item(0)
        p_files_sdcard.page_enable()
    if USBstorage == False:
        menu_files.disable_item(-1)
        p_files_usb.page_disable()
    else:
        menu_files.enable_item(-1)
        p_files_usb.page_enable()


def create_QR(text, file_name):
    import qrcode

    qr = qrcode.QRCode(
        version=3,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=4,
        border=1
    )

    qr.add_data(text)
    qr.make(fit=True)
    img = qr.make_image()
    img.save(file_name)


def check_wifi(ifname, item_num):
    # print "checking wifi"
    if ifname == "wlan0":
        global currentIP
        file_path = IMG_PATH_QRwlan0
        p = subprocess.Popen("ifconfig wlan0 | grep addr: | cut -d : -f 2 | cut -d ' ' -f 1", shell=True,
                             stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        p.wait()
        res = p.stdout.readlines()
        if len(res)>0:
            res = res[0][0:-1]
        else:
            return

        if currentIP == '':
            currentIP = res
        elif currentIP == res:
            return

        if len(res) > 7:
            STA_IP.set_text("http://" + res)
            create_QR("http://" + res, file_path)
            p = subprocess.Popen('iwconfig wlan0 | grep ESSID: | cut -d \\" -f 2', shell=True,
                                 stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            p.wait()
            res = p.stdout.readlines()[0]
            if res[-1] == '\n' or res[-1] == '\r':
                res = res[0:-1]

            STA_SSID.set_text("SSID:" + res)
            menu_connection.enable_item(item_num)
            Img_QR_STA = image(47, 0, [IMG_PATH_QRwlan0])
            p_QR_STA.add_show(Img_QR_STA)
            home_status_bar.add_status('wifi')
        else:
            logger.error("get wlan0 ERROR")
            menu_connection.disable_item(item_num)
            home_status_bar.del_status('wifi')

    elif ifname == "ra0":
        p = subprocess.Popen("cat /sys/class/net/ra0/operstate", shell=True,
                             stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        p.wait()
        res = p.stdout.readlines()[0]

        if "up" in res or "unknown" in res:
            p = subprocess.Popen('cat /etc/Wireless/RT2870AP/RT2870AP.dat | grep ^SSID= | cut -d = -f 2', shell=True,
                             stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            p.wait()
            res = p.stdout.readlines()[0][0:-1]
            AP_SSID.set_text("SSID:" + res)
            menu_connection.enable_item(item_num)
            home_status_bar.add_status('ap')
        else:
            logger.error("get wlan0 ERROR")
            menu_connection.disable_item(item_num)
            home_status_bar.del_status('ap')

def power_down():
    if g_p_.mostfun.state == "printing" or g_p_.mostfun.state == "pause":
        logger.warning("power down,save running task")
        jump2page(p_power_down)
        save_printing(True)
    else:
        logger.warning("power down")
        jump2page(p_bye)
        # os.system('halt')


def LCDsleep():
    global screen
    global Lcd_sleep
    Lcd_sleep = True
    sleep(0.05)
    screen.save(PATH_FRAME_BUFFER)
    sleep(0.02)
    os.kill(TFT_PID, 2)
    # sleep(0.05)

def LCDweakup():
    global sleep_time
    global Lcd_sleep
    Lcd_sleep = False
    sleep_time = time()


def bibi(sustain, times):
    p = subprocess.Popen(["/mostfun/buzzer", str(sustain), str(times)], \
                         stdin=subprocess.PIPE, stdout=subprocess.PIPE, \
                         stderr=subprocess.PIPE, shell=False)

def take_photo():
    print "take photo"
    logger.info('take photo')
    subprocess.call('echo 0 > /tmp/webcom', shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

def finishSendMail(print_info):
    file_name = print_info[1].split('/')[-1]
    info = 'Model Name:' + file_name + \
            '  Start Time:' + print_info[2] + \
            '  Finish Time:' + print_info[3]
    take_photo()
    take_photo()
    sleep(0.5)
    if os.path.exists(r"/tmp/0.jpg"):
        res = mail.send_mail(title='Print Finished', content=info, attachments=r'/tmp/0.jpg')
        logger.info('print finish and take photo ok')
    else:
        res = mail.send_mail(title='Print Finished', content=info, attachments='')
        logger.error('print finish but take photo failed')

    if res:
        logger.info('ptint finish and send mail ok')
    else:
        logger.error('print finish but send mail failed')


Black_light.dir(mraa.DIR_OUT)
#sdPin.dir(mraa.DIR_IN)
black_light("on")
# UI start

with open("/var/run/TFT_8340.pid","r") as TFT:
    TFT_PID = int(TFT.read())
print "TFT PID:" + str(TFT_PID)

p_logo = page(PATH_LOGO, enablehoming=False)
p_continue = page(PATH_BLACK, enablehoming=False)
p_connection_menu = page(PATH_BLACK)
p_QR_AP = page(PATH_QR_AP)
p_QR_STA = page(PATH_QR_STA)
p_language = page(PATH_BLACK)
p_version = page(PATH_SETTING)

p_main_menu = page(PATH_BLACK)
p_files_menu = page(PATH_BLACK)
p_files_local = page(PATH_BLACK)
p_files_sdcard = page(PATH_BLACK)
p_files_usb = page(PATH_BLACK)
p_files_paused = page(PATH_BLACK)

p_setting_menu = page(PATH_BLACK)
p_auto_leveling = page(PATH_LEVELING, enablehoming=True)
p_leveling_set = page(PATH_ADJUSTING, enablehoming=False)
p_refill = page(PATH_REFILLTEST, ("ready", "printing", "pause"), enablehoming=False)
p_pullout = page(PATH_EXTRUD, ("ready", "printing", "pause"), enablehoming=False)
p_feedin = page(PATH_EXTRUD, ("ready", "printing", "pause"), enablehoming=False)
p_test = page(PATH_TEST, ("ready", "printing", "pause"), enablehoming=False)

p_heating = page(PATH_HEATING, ("printing", "pause"), enablehoming=False)
p_printing = page(PATH_BLACK, ("printing", "pause"))
p_printing_ctl_menu = page(PATH_BLACK, ("printing", "pause"))
p_cancel_printing = page(PATH_ATTENTION, ("printing", "pause"))
p_save_printing = page(PATH_ATTENTION, ("printing", "pause"))
p_pause_printing = page(PATH_ATTENTION, ("printing", "pause"))
p_resume_printing = page(PATH_ATTENTION, ("printing", "pause"))

p_power_down = page(PATH_POEWRDOWN, ("ready", "printing", "pause"))
p_bye = page(PATH_BLACK, ("ready", "printing", "pause"))

p_confirm = page(PATH_BLACK,enablehoming=False)
p_waiting = page(PATH_BLACK, ("ready", "printing", "pause"),enablehoming=False)
p_warning = page(PATH_WARNING, ("ready", "printing", "pause"),enablehoming=False)
p_error = page(PATH_ERROR, ("ready", "printing", "pause","error"),enablehoming=True)
p_upgrading = page(PATH_UPGRADE, ("ready", "printing", "pause"),enablehoming=False)

p_home = p_main_menu
p_env = static_p()


UI_printing = [p_printing, p_printing_ctl_menu, p_cancel_printing, p_save_printing, p_pause_printing, p_resume_printing]

# begin build pages


please_waiting = textbox("center", UIconfig["mesg"]["wait"], "middle", font_cn18)
p_waiting.add_show(please_waiting)

warning_info = textbox([5, 72, 215, 175], "", "middle", font_cn16)
p_warning.add_show(warning_info)

error_info = textbox([10,115,210,175], "ERROR", "middle", font_cn16)
p_error.add_show(error_info)

upgrading_info = textbox([5,120,215,170], "getting upgrade...", "middle", font_cn18)
p_upgrading.add_show(upgrading_info)

Btn_contimue_interrupt_YES = button((150, 125), (36, 60), UIconfig["button"]["YES"], continue_interrupt)
Btn_contimue_interrupt_YES.set_warning()
Btn_contimue_interrupt_save = button((80, 125), (36, 60), UIconfig["button"]["save"], save_interrupt)
Btn_contimue_interrupt_skip = button((10, 125), (36, 60), UIconfig["button"]["skip"], skip_interrupt)
p_continue.add_ele(Btn_contimue_interrupt_skip)
p_continue.add_ele(Btn_contimue_interrupt_save)
p_continue.add_ele(Btn_contimue_interrupt_YES)
file_name_rolling = rolling_text(2, Current_gcode_PATH, font_mdcn30, 'l')
p_continue.add_show(file_name_rolling)
continue_msg = textbox((10, 36, 210, 68), UIconfig["mesg"]["continue"], "middle", font_cn20)
p_continue.add_show(continue_msg)
time_msg = textbox((10, 68, 200, 96), UIconfig["mesg"]["autostart"], "middle", font_cn18)
p_continue.add_show(time_msg)
clock = timer_show((98, 102), 30)
p_continue.add_show(clock)
p_continue.set_timeout(30, continue_interrupt)

local_files = file_list("files", PATH_LOCAL)
local_files_msg = textbox((5, 5, 210, 24), UIconfig["mesg"]["localfiles"], "left", font_cn20)
p_files_local.add_ele(local_files)
p_files_local.add_show(local_files_msg)

sdcard_files = file_list("files", PATH_SDCARD)
sdcard_files_msg = textbox((5, 5, 210, 24), UIconfig["mesg"]["sdfiles"], "left", font_cn20)
p_files_sdcard.add_ele(sdcard_files)
p_files_sdcard.add_show(sdcard_files_msg)

usb_files = file_list("files", PATH_USB)
usb_files_msg = textbox((5, 5, 210, 24), UIconfig["mesg"]["usbfiles"], "left", font_cn20)
p_files_usb.add_ele(usb_files)
p_files_usb.add_show(usb_files_msg)

paused_files = file_list("files", PATH_PAUSED)
paused_files_msg = textbox((5, 5, 210, 24), UIconfig["mesg"]["pausedfiles"], "left", font_cn20)
p_files_paused.add_ele(paused_files)
p_files_paused.add_show(paused_files_msg)

main_menu = menu("mainmenu", [p_connection_menu, p_files_local, p_setting_menu, p_files_paused, p_files_menu])
home_status_bar = status_bar()
if printedsecs > printedalarm:
    home_status_bar.add_status('repair')
p_main_menu.add_ele(home_status_bar)
p_main_menu.add_ele(main_menu)

menu_files = menu("filesmenu", [p_files_sdcard, p_files_usb])
p_files_menu.add_ele(menu_files)

menu_printing_ctl = menu("pctlmenu",
                         [p_pause_printing, p_resume_printing, p_heating, p_save_printing, p_cancel_printing, p_refill])
p_printing_ctl_menu.add_ele(menu_printing_ctl)
p_printing_ctl_menu.set_timeout(15, jump2page, p_home)

menu_connection = menu("wifimenu", [p_QR_AP, p_QR_STA,p_language,p_version])
p_connection_menu.add_ele(menu_connection)

menu_setting = menu("settingmenu", [p_refill, p_auto_leveling])
p_setting_menu.add_ele(menu_setting)

Img_leveling = image(0, 0, [IMG_LEVELING0, IMG_LEVELING1, IMG_LEVELING2, IMG_LEVELING3, IMG_LEVELING4, IMG_LEVELING5,
                            IMG_LEVELING6, IMG_LEVELING7, IMG_LEVELING8, IMG_LEVELING9, IMG_LEVELING10, IMG_LEVELING9,
                            IMG_LEVELING8, IMG_LEVELING7,
                            IMG_LEVELING6, IMG_LEVELING5], 0)
p_auto_leveling.add_show(Img_leveling)
Btn_check_start = button((20, 130), (36, 78), UIconfig["button"]["start"], level_start)
Btn_check_start.set_warning()
Btn_adjusting = button((120, 130), (36, 78), UIconfig["button"]["adjust"], jump2page, p_leveling_set)
Btn_adjusting.disable()

# p_auto_leveling.add_ele(Btn_check_done)
p_auto_leveling.add_ele(Btn_adjusting)
p_auto_leveling.add_ele(Btn_check_start)

mesg_leveling = textbox((140, 40, 210, 100), UIconfig["mesg"]["leveling"], "middle", font_bdcn20)
p_auto_leveling.add_show(mesg_leveling)

Btn_up = button_img((137, 50), [BTN_PATH_UP0, BTN_PATH_UP1, BTN_PATH_UP0], Z_up)
Btn_down = button_img((137, 90), [BTN_PATH_DOWN0, BTN_PATH_DOWN1, BTN_PATH_DOWN0], Z_down)
Btn_handcheck_apply = button((131, 130), (36, 78), UIconfig["button"]["apply"], level_hand_check_apply)
Btn_handcheck_cancel = button((15, 130), (36, 80), UIconfig["button"]["cancel"], level_hand_check_cancel)
Btn_handcheck_apply.set_warning()
p_leveling_set.add_ele(Btn_down)
p_leveling_set.add_ele(Btn_handcheck_cancel)
p_leveling_set.add_ele(Btn_handcheck_apply)
p_leveling_set.add_ele(Btn_up)

img_bord = shap_line([15,113,132,113],color=COLOR_WHIT,width=3)
img_bord.set_range([-1,1,-20,10])

p_leveling_set.add_show(img_bord)

Btn_ex_up = button_img((155, 15), [BTN_PATH_TEMP_UP0, BTN_PATH_TEMP_UP1, BTN_PATH_TEMP_UP0], ex_temper_up)
Btn_ex_down = button_img((155, 51), [BTN_PATH_TEMP_DOWN0, BTN_PATH_TEMP_DOWN1, BTN_PATH_TEMP_DOWN0], ex_temper_down)
Btn_bed_up = button_img((155, 67), [BTN_PATH_TEMP_UP0, BTN_PATH_TEMP_UP1, BTN_PATH_TEMP_UP0], bed_temper_up)
Btn_bed_down = button_img((155, 103), [BTN_PATH_TEMP_DOWN0, BTN_PATH_TEMP_DOWN1, BTN_PATH_TEMP_DOWN0], bed_temper_down)

Btn_ex_up.add_images([IMG_HEATINGEX1,IMG_HEATINGEX2],(0,0))
# Btn_ex_down.add_images([IMG_HEATINGEX1,IMG_HEATINGEX2],(0,0))
Btn_bed_up.add_images([IMG_HEATINGBED1,IMG_HEATINGBED2],(0,130))
# Btn_bed_down.add_images([IMG_HEATINGBED1,IMG_HEATINGBED2],(0,130))

p_heating.add_ele(Btn_ex_up)
p_heating.add_ele(Btn_ex_down)
p_heating.add_ele(Btn_bed_up)
p_heating.add_ele(Btn_bed_down)
# r_box_ex = rolling_box((155,25),(180,240),3,[IMG_PATH_ROLLING_BOX0,IMG_PATH_ROLLING_BOX0],set_ex_temper)
# r_box_bed = rolling_box((155,80),(0,120),10,[IMG_PATH_ROLLING_BOX0,IMG_PATH_ROLLING_BOX0],set_bed_temper)
# r_box_ex.add_images([IMG_HEATINGEX1,IMG_HEATINGEX2],(0,0))
# r_box_bed.add_images([IMG_HEATINGBED1,IMG_HEATINGBED2],(0,130))

# p_heating.add_ele(r_box_ex)
# p_heating.add_ele(r_box_bed)

Btn_heating_back = button((130, 125), (36, 80), UIconfig["button"]["back"], back2printing)
# Btn_heating_back.set_warning()
p_heating.add_ele(Btn_heating_back)

# tmper_E_msg = textbox((90, 15, 150, 60), UIconfig["mesg"]["extruder"], "left", font_cn20)
tmper_E_T = textbox((102, 32, 140, 50), u"-.-", "left", font_cn18)
tmper_E_T_target = textbox((155, 32, 190, 48), u"-.-", "left", font_cn18)
# tmper_B_msg = textbox((90, 83, 150, 103), UIconfig["mesg"]["bed"], "left", font_cn20)
tmper_B_T = textbox((102, 84, 140, 102), u"-.-", "left", font_cn18)
tmper_B_T_target = textbox((155, 84, 190, 100), u"-.-", "left", font_cn18)
# p_heating.add_show(tmper_E_msg)
p_heating.add_show(tmper_E_T)
p_heating.add_show(tmper_E_T_target)
# p_heating.add_show(tmper_B_msg)
p_heating.add_show(tmper_B_T)
p_heating.add_show(tmper_B_T_target)
Img_heating = image(35, 110, [IMG_HEATING1, IMG_HEATING2])
p_heating.add_show(Img_heating)
 
printer_state = printing("printer", g_p_.mostfun)
p_printing.add_ele(printer_state)
print_name_rolling = rolling_text(0, Current_gcode_PATH, font_mdcn28, 'l')
p_printing.add_show(print_name_rolling)

Btn_cancel_print_NO = button((20, 125), (36, 64), UIconfig["button"]["NO"], jumpback)
Btn_cancel_print_YES = button((135, 125), (36, 64), UIconfig["button"]["YES"], cancel_printing)
Btn_cancel_print_YES.set_warning()
p_cancel_printing.add_ele(Btn_cancel_print_YES)
p_cancel_printing.add_ele(Btn_cancel_print_NO)
cancel_msg = textbox("center", UIconfig["mesg"]["cancel"], "middle", font_cn18)
p_cancel_printing.add_show(cancel_msg)

Btn_pause_print_NO = button((20, 125), (36, 64), UIconfig["button"]["NO"], jumpback)
Btn_pause_print_YES = button((135, 125), (36, 64), UIconfig["button"]["YES"], pause_printing)
Btn_pause_print_YES.set_warning()
p_pause_printing.add_ele(Btn_pause_print_NO)
p_pause_printing.add_ele(Btn_pause_print_YES)
pause_msg = textbox("center", UIconfig["mesg"]["pause"], "middle", font_cn18)
p_pause_printing.add_show(pause_msg)

Btn_resume_print_NO = button((20, 125), (36, 64), UIconfig["button"]["NO"], jumpback)
Btn_resume_print_YES = button((135, 125), (36, 64), UIconfig["button"]["YES"], resume_printing)
Btn_resume_print_YES.set_warning()
p_resume_printing.add_ele(Btn_resume_print_NO)
p_resume_printing.add_ele(Btn_resume_print_YES)
resume_msg = textbox("center", UIconfig["mesg"]["resume"], "middle", font_cn18)
p_resume_printing.add_show(resume_msg)

Btn_save_print_NO = button((20, 125), (36, 64), UIconfig["button"]["NO"], jumpback)
Btn_save_print_YES = button((120, 125), (36, 64), UIconfig["button"]["YES"], save_printing)
Btn_save_print_YES.set_warning()
p_save_printing.add_ele(Btn_save_print_NO)
p_save_printing.add_ele(Btn_save_print_YES)
save_msg = textbox("center", UIconfig["mesg"]["stop"], "middle", font_cn18)
p_save_printing.add_show(save_msg)

Btn_refill_quit = button((20, 125), (36, 64), UIconfig["button"]["quit"], jump2page, p_main_menu)
Btn_refill_next = button((135, 125), (36, 64), UIconfig["button"]["next"], jump2page, p_pullout)
Btn_refill_next.set_warning()
Btn_refill_next.disable()
p_refill.add_ele(Btn_refill_quit)
p_refill.add_ele(Btn_refill_next)
refill_msg = textbox((125, 45, 215, 100), UIconfig["mesg"]["heating"], font_cn16)
p_refill.add_show(refill_msg)
# temp_msg = textbox((10,90,210,115),"",font_cn18)
# p_refill.add_show(temp_msg)
temp_bar = process_bar((110, 97), (110, 32), COLOR_RED)
p_refill.add_show(temp_bar)

Btn_pullout_next = button((135, 125), (36, 64), UIconfig["button"]["next"], jump2page, p_feedin)
Btn_pullout_next.set_warning()
p_pullout.add_ele(Btn_pullout_next)
Img_pullout = image(0, 0, [IMG_PATH_PULLOUT, IMG_PATH_PULLOUT1, IMG_PATH_PULLOUT2])
p_pullout.add_show(Img_pullout)
pullout_msg = textbox((133, 30, 210, 120), UIconfig["mesg"]["pullout"], "middle", font_cn16)
p_pullout.add_show(pullout_msg)

Btn_feedin_next = button((135, 125), (36, 64), UIconfig["button"]["next"], jump2page, p_test)
Btn_feedin_next.set_warning()
p_feedin.add_ele(Btn_feedin_next)
Img_feedin = image(0, 0, [IMG_PATH_FEEDIN, IMG_PATH_FEEDIN1, IMG_PATH_FEEDIN2])
p_feedin.add_show(Img_feedin)
feedin_msg = textbox((130, 30, 210, 120), UIconfig["mesg"]["feedin"], "middle", font_cn16)
p_feedin.add_show(feedin_msg)

Btn_refill_finish = button((130, 125), (36, 74), UIconfig["button"]["OK"], jump2page, p_home)
Btn_extrud_test = button((20, 125), (36, 64), UIconfig["button"]["test"], extrud)
Btn_extrud_test.set_warning()
p_test.add_ele(Btn_refill_finish)
p_test.add_ele(Btn_extrud_test)
test_msg = textbox((125, 35, 210, 120), UIconfig["mesg"]["test"], "middle", font_cn16)
Img_ex_test = image(0, 0, [IMG_PATH_EX1, IMG_PATH_EX2, IMG_PATH_EX3, IMG_PATH_EX4], 0)
p_test.add_show(test_msg)
# print UIconfig["mesg"]["test"].decode('string-escape')
p_test.add_show(Img_ex_test)

Btn_confirm_YES = button((135, 125), (36, 64), UIconfig["button"]["print"], begin_printing)
Btn_confirm_YES.set_warning()
Btn_confirm_NO = button((15, 125), (36, 80), UIconfig["button"]["cancel"], jumpback)
comfirm_msg = textbox((10, 10, 210, 120), "", "middle", font_mdcn24)
p_confirm.add_show(comfirm_msg)
p_confirm.add_ele(Btn_confirm_NO)
p_confirm.add_ele(Btn_confirm_YES)

Img_QR_AP = image(47, 0, [IMG_PATH_QRwlan1])
p_QR_AP.add_show(Img_QR_AP)
AP_SSID = textbox((0, 126, 219, 150), UIconfig["mesg"]["noconnect"], "middle", font_cn16)
AP_IP = textbox((0, 150, 219, 175), "http://192.168.42.1", "middle", font_cn16)
p_QR_AP.add_show(AP_SSID)
p_QR_AP.add_show(AP_IP)
p_QR_AP.add_ele(p_env)

Img_QR_STA = image(47, 0, [IMG_PATH_QRwlan0])
p_QR_STA.add_show(Img_QR_STA)
STA_SSID = textbox((0, 126, 219, 150), UIconfig["mesg"]["noconnect"], "middle", font_cn16)
STA_IP = textbox((0, 150, 219, 175), "http://", "middle", font_cn16)
p_QR_STA.add_show(STA_IP)
p_QR_STA.add_show(STA_SSID)
p_QR_STA.add_ele(p_env)

lang_cn_msg = textbox((5, 25, 215, 55), "请选择语言", "middle", font_cn16)
lang_en_msg = textbox((5, 55, 215, 85), "Please choose language", "middle", font_cn16)
Btn_setEN = button((10, 130), (36, 89), "English", set_language, "en")
Btn_setCH = button((130, 130), (36, 80), u"中文", set_language, "ch")
p_language.add_show(lang_cn_msg)
p_language.add_show(lang_en_msg)
p_language.add_ele(Btn_setEN)
p_language.add_ele(Btn_setCH)

p = subprocess.Popen("uname -r", shell=True,stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
p.wait()
res = p.stdout.readlines()[0]
ver_str = UIconfig["mesg"]["sysver"]+res
p = subprocess.Popen("opkg list-installed | grep mostfun-pro-panel", shell=True,stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
p.wait()
res = p.stdout.readlines()[0]
if len(res) > 20:
    res = res[20:-1]
ver_str += UIconfig["mesg"]["panelver"]+res+'\n'
p = subprocess.Popen("opkg list-installed | grep marlin", shell=True,stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
p.wait()
res = p.stdout.readlines()[0][9:-1]
ver_str += UIconfig["mesg"]["avrver"]+res
version = textbox((0, 80, 219, 175), ver_str, "left", font_cn16)
p_version.add_show(version)
p_version.add_ele(p_env)

power_down_msg = textbox((0, 120, 219, 150), UIconfig["mesg"]["save"], "middle", font_cn20)
p_power_down.add_show(power_down_msg)

bye_msg = textbox("center", UIconfig["mesg"]["bye"], "middle", font_mdcn24)
p_bye.add_show(bye_msg)


def m_UI():
    global Lcd_sleep
    global Current_page

    bibi(100, 2)

    firstuse = getINI("other", "firstuse")
    if firstuse == '1':
        print "first use"
        jump2page(p_language)
        modINI("other","firstuse", "0")
    else:
        jump2page(p_main_menu)

    # Interrupted = check_interrupt()
    # if Interrupted:
    #     jump2page(p_continue)
    # else:
    #     jump2page(p_main_menu)
    # Current_page.flush_page()

    while True:
        if Lcd_sleep == False:
            if not g_p_.mostfun.get_state() in Current_page.owner:
                state = g_p_.mostfun.get_state()
                if state == "printing" or state == "pause":
                    p_home = p_printing
                elif state == "error":
                    home_status_bar.add_status('error')
                    p_home = p_main_menu
                elif state == "updating":
                    p_home = p_upgrading

                else:
                    p_home = p_main_menu

                jump2page(p_home)

            Current_page.flush_page()
            sleep(0.02)
            os.kill(TFT_PID, 2)
            sleep(0.02)

        else:
            sleep(0.1)


def input_env():
    mouse_exist = True
    try:
        inputdev_mouse = InputDevice('/dev/input/mouse0')
    except:
        mouse_exist = False
        print "no mouse found"
    

    def input_key():
        global Current_page
        global Lcd_sleep
        global sleep_time
        main_btn_state = 0
        inputdev_key = InputDevice('/dev/input/event1')
        while True:
            select([inputdev_key], [], [])
            for event in inputdev_key.read():
                if Lcd_sleep == False:
                    sleep_time = time()
                    if event.code == 28:
                        if event.value == 0:
                            if main_btn_state == 1:
                                Current_page.click('0')
                            main_btn_state = 0

                        elif event.value == 1:
                            main_btn_state = 1

                        elif event.value == 2:
                            if main_btn_state > 0:
                                main_btn_state += 1
                                if main_btn_state == 5:
                                    Current_page.click('1')
                                    main_btn_state = 0
                else:
                    LCDweakup()

    def input_rotary():
        global Current_page
        global Lcd_sleep
        global sleep_time
        inputdev_rotary = InputDevice('/dev/input/event0')
        while True:
            select([inputdev_rotary], [], [])
            for event in inputdev_rotary.read():
                print event.code
                print event.value
                if Lcd_sleep == False:
                    sleep_time = time()
                    if event.code == 2:
                        if event.value == 1:
                            Current_page.click('<')
                        elif event.value == -1:
                            Current_page.click('>')
                else:
                    LCDweakup()

    # def input_mouse():
    #     global Current_page
    #     global Lcd_sleep
    #     global sleep_time
    #     while True:
    #         select([inputdev_mouse], [], [])
    #         for event in inputdev_mouse.read():
    #             if Lcd_sleep == False:
    #                 if event.code == 272:
    #                     if event.value == 1:
    #                         Current_page.click('0')
    #                 elif event.code == 273:
    #                     if event.value == 1:
    #                         Current_page.click('1')
    #                 elif event.code == 8:
    #                     if event.value == 1:
    #                         Current_page.click('<')
    #                     elif event.value == -1:
    #                         Current_page.click('>')
    #             else:
    #                 LCDweakup()


    thread_input_rotary = threading.Thread(target=input_rotary)
    thread_input_rotary.daemon = True
    thread_input_rotary.start()

    # if mouse_exist:
    #     thread_input_mouse = threading.Thread(target=input_mouse)
    #     thread_input_mouse.daemon = True
    #     thread_input_mouse.start()

    thread_input_key = threading.Thread(target=input_key)
    thread_input_key.daemon = True
    thread_input_key.start()


def globe_env():
    global Current_page
    global Lcd_sleep
    global printedsecs

    while True:
        if time() - sleep_time > LCD_SLEEP_TIMEOUT:
            LCDsleep() 
        printer_mesgs = g_p_.mostfun.UI_box_getter()
        if len(printer_mesgs)>0:
            print "printer mesgs",printer_mesgs
        for mesg in printer_mesgs:
            if mesg.startswith("LEVELING:"):
                if "1" in mesg:
                    # Btn_check_start.disable()
                    # Btn_adjusting.disable()
                    pass

                elif "0" in mesg:
                    Btn_check_start.enable()
                    Btn_adjusting.enable()
                    Img_leveling.play(0)

            elif mesg.startswith("finished:"):
                tmp = str(int(mesg.split(':')[-1])+printedsecs)
                modINI("other","printedsecs", str(int(mesg.split(':')[-1])+printedsecs))

            elif mesg.startswith("taskfinished"):
                print_info = mesg.split(';')
                finishSendMail(print_info)

            elif mesg.startswith("ERROR:"):
                error(UIconfig["mesg"]["error"]+re.search("ERROR:*([0-9]*)", mesg).group(1))

        if Lcd_sleep == False:
            if Current_page == p_main_menu or Current_page == p_files_menu or Current_page == p_files_usb or Current_page == p_files_sdcard:
                check_SD()

            if Current_page == p_main_menu or Current_page == p_connection_menu:
                check_wifi("wlan0", 1)
                check_wifi("ra0", 0)

            # elif Current_page == p_continue:
            #     file_name_rolling.set_text(Current_gcode_PATH.split(r'/')[-1])

            # elif Current_page == p_main_menu or Current_page == p_files_menu:

            if Current_page == p_refill:
                temp_bar.set_persent(g_p_.mostfun.get_extruderTemp() / 230.0)
                if g_p_.mostfun.get_extruderTemp() < 180:
                    Btn_refill_next.disable()
                else:
                    Btn_refill_next.enable()
            if Current_page == p_heating:
                # else:
                tmper_E_T.set_text(str(g_p_.mostfun.get_extruderTemp()))
                tmper_E_T_target.set_text(str(g_p_.mostfun.get_extruderTargetTemp()))
                    # str(g_p_.mostfun.get_extruderTemp()) + '/' + str(g_p_.mostfun.get_extruderTargetTemp()) + u'°C')
                tmper_B_T.set_text(str(g_p_.mostfun .get_bedTemp()))
                tmper_B_T_target.set_text(str(g_p_.mostfun.get_bedTargetTemp()))
                    # str(g_p_.mostfun.get_bedTemp()) + '/' + str(g_p_.mostfun.get_bedTargetTemp()) + u'°C')
                if p_heating.enable_autojump:
                    if g_p_.mostfun.is_hot() == True:
                        # p_home = p_printing
                        back2printing()
                        # g_p_.mostfun.send_command(["M107"])

            if Current_page == p_printing:
                printer_state.refresh_printer_state()

            sleep(0.2)
        else:
            sleep(0.2)


def UI_monitor():
    thread_UI = threading.Thread(target=m_UI)
    thread_UI.daemon = True
    thread_UI.start()
    sleep(0.1)

    thread_input_env = threading.Thread(target=input_env)
    thread_input_env.daemon = True
    thread_input_env.start()
    sleep(0.1)

    thread_globe_env = threading.Thread(target=globe_env)
    thread_globe_env.daemon = True
    thread_globe_env.start()
