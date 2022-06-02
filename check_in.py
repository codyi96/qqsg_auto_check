# -*- coding: utf-8 -*-

from selenium.common.exceptions import TimeoutException
from verify_capcha import Tencent
from verify_capcha import EC
from verify_capcha import By
import time
import base64
import json

class Tencent_net(Tencent):

    def set_info(self):

        self.browser.get(url=self.url)
        try:
            self.wait.until(EC.presence_of_all_elements_located((
                By.ID, 'loginFrame'
            )))
            # 进入登录子页面
            self.browser.switch_to.frame(
                self.browser.find_element_by_id('loginFrame')
            )
            # qq账号登录
            input_username = self.wait.until(EC.presence_of_element_located((
                By.ID, 'u'
            )))
            # 密码
            input_password = self.wait.until(EC.presence_of_element_located((
                By.ID, 'p'
            )))
            input_username.send_keys(self.username)
            input_password.send_keys(self.password)
            time.sleep(1)
            qq_login_button = self.wait.until(EC.element_to_be_clickable((
                By.ID, 'go'
            )))
            qq_login_button.click()

        except TimeoutException as e:
            print('Error:', e.args)
            self.set_info()


    def end(self):
        #签到
        check_in_button = self.wait.until(EC.element_to_be_clickable((
            By.CLASS_NAME, 'btn-sign-in'
        )))
        check_in_button.click()

if __name__ == '__main__':
    # load account file
    f = open("config.json")
    dict = json.load(f)
    url='https://sg.qq.com/cp/a20200228signin/index.html'
     
  
    for index in range(len(dict['users'])):
        user=dict['users'][index]
        username=user['u']
        password=user['p']
        tencent=Tencent_net(url,username,password)
        tencent.re_start()
