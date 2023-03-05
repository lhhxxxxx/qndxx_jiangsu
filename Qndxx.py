import json
import re
from loguru import logger

import requests
from bs4 import BeautifulSoup


class Qndxx:
    def __init__(self, laravel_session):
        # 需要传入的laravel_session
        self.laravel_session = laravel_session
        # 请求头
        self.UA = "Mozilla/5.0 (iPhone; CPU iPhone OS 15_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 MicroMessenger/8.0.18(0x18001234) NetType/WIFI Language/zh_CN"
        # 江苏省青年大学习接口
        self.loginurl = "https://service.jiangsugqt.org/youth/lesson"
        # 确认信息接口
        self.confirmurl = "https://service.jiangsugqt.org/youth/lesson/confirm"
        # 创建会话
        self.session = requests.session()  # 创建会话
        # 构建用户信息字典
        self.userinfo = {}

    def get_userinfo(self, userinfo):
        for i in userinfo:
            # 解析课程姓名编号单位信息
            info_soup = BeautifulSoup(str(i), 'html.parser')
            item = info_soup.get_text()  # 用户信息
            self.userinfo[item[:4]] = item[5:]

    def confirm(self):
        params = {
            "_token": self.userinfo.get('token'),
            "lesson_id": self.userinfo.get('lesson_id')
        }
        confirm_res = self.session.post(url=self.confirmurl, params=params)
        res = json.loads(confirm_res.text)
        logger.info(f"返回结果:{res}")
        if res["status"] == 1 and res["message"] == "操作成功":
            logger.info("青年大学习已完成")
            logger.info(f"您的信息:{self.userinfo}")
        else:
            raise Exception(f"确认时出现错误:{res['message']}")

    def login(self):
        # 参数
        params = {
            "s": "/youth/lesson",
            "form": "inglemessage",
            "isappinstalled": "0"
        }
        # 构造请求头
        headers = {
            'User-Agent': self.UA,
            'Cookie': "laravel_session=" + self.laravel_session  # 抓包获取
        }
        # 登录
        login_res = self.session.get(url=self.loginurl, headers=headers, params=params)

        if '抱歉，出错了' in login_res.text:
            raise Exception("laravel_session错误")
        # 正则匹配token和lesson_id
        token = re.findall(r'var token ?= ?"(.*?)"', login_res.text)  # 获取js里的token
        lesson_id = re.findall(r"'lesson_id':(.*)", login_res.text)  # 获取js里的token

        self.userinfo['token'] = token[0]
        self.userinfo['lesson_id'] = lesson_id[0]
        # 解析信息确认页面
        login_soup = BeautifulSoup(login_res.text, 'html.parser')
        # 找到用户信息div 课程姓名编号单位
        userinfo = login_soup.select(".confirm-user-info p")
        self.get_userinfo(userinfo)



