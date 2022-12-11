# -*- coding: utf-8 -*-
from selenium.webdriver.support import expected_conditions as EC  # 显性等待
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver import ActionChains
from selenium import webdriver
import numpy as np
import cv2 as cv
import platform
import requests
import random
import time
import os

def get_driver():
    os_type = platform.system()
    root_dir = os.path.dirname(os.path.abspath(__file__))
    drivers_dir = os.path.join(root_dir, 'drivers')
    if os_type == 'Darwin':
        return os.path.join(drivers_dir, 'chromedriver_mac64')
    elif os_type == 'Windows':
        return os.path.join(drivers_dir, 'chromedriver_win32.exe')
    elif os_type == 'Linux':
        return os.path.join(drivers_dir, 'chromedriver_linux64')
    else:
        return None

class Tencent:
    """
    识别tx验证码
    """

    def __init__(self, url, username, password):
        """
        初始化浏览器配置，声明变量

        :param url: 要登录的网站地址
        :param username: 账号
        :param password: 密码
        """
        profile = webdriver.ChromeOptions()  # 配置无头
        profile.add_argument('-headless')
        driver_location = get_driver()
        if driver_location is None:
            print('不支持的系统类型！')
            exit(-1)
        self.browser = webdriver.Chrome(driver_location)
        self.wait = WebDriverWait(self.browser, 20)
        self.url = url  # 目标url
        self.username = username  # 用户名
        self.password = password  # 密码
        self.retry_count = 0 # 重试次数

    def end(self):
        """
        结束后退出，可选

        :return:
        """
        self.browser.quit()

    def set_info(self):
        """
        填写个人信息，在子类中完成

        """
        pass

    def tx_code(self):
        """
        主要部分，函数入口

        :return:
        """
        self.set_info()
        try:
            WebDriverWait(self.browser, 20, 0.5).until(
                EC.presence_of_element_located((By.ID, 'tcaptcha_iframe_dy')))  # 等待 iframe
        except:
            print("load  tcaptcha_iframe_dy failed")
            return False
        self.browser.switch_to.frame(
            self.browser.find_element_by_id('tcaptcha_iframe_dy'))  # 加载 iframe
        time.sleep(0.5)
        # 捡取验证图
        slide_bg = self.browser.find_element_by_xpath(
            '//div[@id="slideBg"]').value_of_css_property('background-image').lstrip('url("').rstrip('")')
        # 捡取滑块
        slide_block = self.browser.find_element_by_xpath(
            '//div[@class="tc-fg-item" and contains(@style,"cap_union_new_getcapbysig?img_index=0")]').value_of_css_property('background-image').lstrip('url("').rstrip('")')
        # 保存验证图+滑块
        if self.save_img(slide_bg, 'bg') and self.save_img(slide_block, 'block'):
            dex = self.get_pos() # 获取滑动距离
            if dex:
                track_list = self.get_track(dex) # 获取滑动路径
                time.sleep(0.5)
                slid_ing = self.browser.find_element_by_xpath(
                    '//img[@class="tc-slider-bg unselectable"]')  # 滑块定位
                ActionChains(self.browser).click_and_hold(
                    on_element=slid_ing).perform()  # 鼠标按下
                time.sleep(0.2)
                print('轨迹', track_list)
                for track in track_list:
                    ActionChains(self.browser).move_by_offset(
                        xoffset=track, yoffset=0).perform()  # 鼠标移动到距离当前位置（x,y）
                time.sleep(1)
                ActionChains(self.browser).release(
                    on_element=slid_ing).perform()  # print('第三步,释放鼠标')
                time.sleep(10)
                # 判断是否验证成功
                try:
                    if (self.browser.find_element_by_xpath('//a[@class="btn-sign-in"]')):
                        return True
                except:
                    self.re_start()
                else:
                    self.re_start()
            else:
                self.re_start()
        else:
            print('缺口图片捕获失败')
            return False

    @staticmethod
    def save_img(img_url, type):
        """
        保存图片

        :param img_url: 图片url
        :param type: 类型
        :return: bool类型，是否被保存
        """
        try:
            img = requests.get(img_url).content
            file_name = type + '.jpeg'
            with open(file_name, 'wb') as f:
                f.write(img)
            return True
        except:
            return False

    @staticmethod
    def get_pos():
        """识别缺口
        注意：网页上显示的图片为缩放图片，缩放 50% 所以识别坐标需要 0.5
        """
        background_pic = cv.imread('bg.jpeg', 0) # 保存验证图
        slider_pic = cv.imread('block.jpeg', 0) # 保存滑块
        slider_pic = slider_pic[500:500+120, 140:140+120] # 下发的滑块是个组合图，需要把缺口图片裁剪出来
        width, height = slider_pic.shape[::-1] # 滑块宽高
        background_pic = cv.GaussianBlur(background_pic, (5, 5), 0)
        slider_pic = cv.GaussianBlur(slider_pic, (5, 5), 0)
        background_pic = cv.Canny(background_pic, 200, 400)
        slider_pic = cv.Canny(slider_pic, 200, 400)
        result = cv.matchTemplate(background_pic, slider_pic, cv.TM_CCORR_NORMED) # 相似计算
        min_val, max_val, min_loc, max_loc = cv.minMaxLoc(result)
        # 画出识别区域 调试用
        # br = (max_loc[0] + width, max_loc[1] + height)
        # cv.rectangle(background_pic, max_loc, br, [255, 255, 255])
        # cv.imshow('image', background_pic)
        # cv.waitKey()
        # 获取图片的缺口位置
        top, left = np.unravel_index(result.argmax(), result.shape)
        # 下发图片为端展图片的两倍，故这里日志和距离返回值都需要除以2
        print("当前滑块的缺口位置：", (left, top, left + width / 2, top + height / 2))
        print("滑动距离：", max_loc[0])
        return max_loc[0] / 2

    @staticmethod
    def get_track(distance):
        """模拟轨迹
        """
        distance -= 25  # 扣除初始位置
        # 初速度
        v = 0
        # 单位时间为0.2s来统计轨迹，轨迹即0.2内的位移
        t = 0.2
        # 位移/轨迹列表，列表内的一个元素代表0.2s的位移
        tracks = []
        # 当前的位移
        current = 0
        # 到达mid值开始减速
        mid = distance * 7 / 8

        # distance += 10  # 先滑过一点，最后再反着滑动回来
        # a = random.randint(1,3)
        while current < distance:
            if current < mid:
                # 加速度越小，单位时间的位移越小,模拟的轨迹就越多越详细
                a = random.randint(2, 4)  # 加速运动
            else:
                a = -random.randint(1, 3)  # 减速运动

            # 初速度
            v0 = v
            # 0.2秒时间内的位移
            s = v0 * t + 0.5 * a * (t ** 2)
            # 当前的位置
            current += s
            # 添加到轨迹列表
            tracks.append(round(s))

            # 速度已经达到v,该速度作为下次的初速度
            v = v0 + a * t

        # # 反着滑动到大概准确位置
        # for i in range(4):
        #     tracks.append(-random.randint(2, 3))
        # for i in range(4):
        #     tracks.append(-random.randint(1, 3))
        return tracks

    def move_to(self, index):
        """
        移动滑块

        :param index:
        :return:
        """
        pass

    def re_start(self):
        """
        准备开始

        :return: None
        """
        if (self.retry_count <= 5):
            self.retry_count += 1
            self.tx_code()

        self.end()
