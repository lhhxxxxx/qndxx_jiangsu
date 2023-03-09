from loguru import logger

import requests


class Qndxx:
    def __init__(self, laravel_session):
        # 需要传入的laravel_session
        self.laravel_session = laravel_session
        # 请求头
        self.UA = "Mozilla/5.0 (Linux; Android 13; 22127RK46C Build/TKQ1.220905.001; wv) AppleWebKit/537.36 (KHTML, " \
                  "like Gecko) Version/4.0 Chrome/107.0.5304.141 Mobile Safari/537.36 XWEB/5015 MMWEBSDK/20230202 " \
                  "MMWEBID/3840 MicroMessenger/8.0.33.2320(0x2800213D) WeChat/arm64 Weixin NetType/WIFI " \
                  "Language/zh_CN ABI/arm64"
        # 江苏省青年大学习成绩单接口
        self.cjdListUrl = "https://service.jiangsugqt.org/api/cjdList"
        # 江苏省青年大学习接口
        self.doLessonUrl = "https://service.jiangsugqt.org/api/doLesson"
        # 创建会话
        self.session = requests.session()
        # 是否已经学习
        self.has_learn = ""
        # 课程id
        self.lesson_id = ""

    def do_qndxx(self):
        # 参数
        params = {
            "lesson_id": self.lesson_id
        }

        res = self.session.post(url=self.doLessonUrl, params=params)
        res = res.json()

        if res["status"] == 1 and res["message"] == "操作成功":
            logger.info("青年大学习已完成")
        else:
            raise Exception(f"确认时出现错误:{res['message']}")

    def get_latest_data(self):
        # 参数
        params = {
            "page": "1",
            "limit": "20"
        }
        # 构造请求头
        headers = {
            'User-Agent': self.UA,
            'Cookie': "laravel_session=" + self.laravel_session
        }
        # 获取成绩单
        res = self.session.post(url=self.cjdListUrl, headers=headers, params=params)
        res = res.json()

        if not (res["status"] == 1 and res["message"] == "操作成功"):
            raise Exception("laravel_session错误")

        self.has_learn = res["data"][0]["has_learn"]
        self.lesson_id = res["data"][0]["id"]

    def start(self):
        # 获取最新的一次课程
        self.get_latest_data()
        if self.has_learn == '1':
            logger.info("已完成过青年大学习")
            return
        self.do_qndxx()
