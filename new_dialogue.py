import aiml
from datetime import timedelta
from datetime import datetime
import locale

import os
from tuling import Tuling
from weather import WeatherHandler
class Dialogue(object):
    def __init__(self, aiml_data_dir = 'aiml_data'):
        self._WEATHER_HANDLER = WeatherHandler()
        self._TULING = Tuling()
        try:
            datetime.now().strftime('%Y年%m月%d日')
        except UnicodeEncodeError:
            locale.setlocale(locale.LC_CTYPE,'chinese')

        self._brain = aiml.Kernel()
        pwd = os.path.abspath(os.curdir)
        os.chdir(os.path.join(pwd,aiml_data_dir))
        self._brain.learn("std-startup.xml")
        self._brain.respond('load aiml b')
        os.chdir(pwd)
        self._task_handler={
            '天气':self._get_weather,
            '日期':self._get_date,
            '时间':self._get_time,
        }
    def _get_weather(self,*args):
        try:
            location = args[0]
        except:
            location = '杭州'
        wh = self._WEATHER_HANDLER
        return wh.get_response(location)
    def _get_time(self,*args):
        now = datetime.now()
        result ='现在是'+now.strftime("%H点%M分")
        return result
    def _get_date(self,*args):

        try:
            interval =  args[0]
        except:
            interval = '今天'
        interval_map = {
            '前天':-2,
            '昨天':-1,
            '今天':0,
            '明天':1,
            '后天':2
        }
        delta = timedelta(days= interval_map.get(interval,0))
        result = (datetime.now()+delta).strftime("%Y年%m月%d日")
        return interval+'是'+result


    def respond(self,sentence):
        # 输入为空，直接返回
        if not sentence:
            return '说点什么吧'
        # AIML规则匹配获取回复
        final_rsp = self._brain.respond(sentence)
        # 特殊指令
        if final_rsp[:4] == '实时查询':
            params = final_rsp.split()
            # 获取任务名
            name = params[1]
            rsp = ''
            # 获取对应处理该任务的函数对象
            if name in self._task_handler:
                task_handler = self._task_handler[name]
            try:
                # 获取函数参数
                args = params[2:]
                # 执行函数
                rsp = task_handler(*args)
            except Exception as e:
                pass
            final_rsp = rsp
        elif final_rsp == '':
            final_rsp = self._TULING.respond(sentence)
        if final_rsp == '暂不支持':
            final_rsp = self._TULING.respond(sentence)
        final_rsp = final_rsp or '我还小，你说的我还不懂'
        return final_rsp

def main():
    dlg = Dialogue()
    while True:
        input_ = input(">>>")
        rsp= dlg.respond(input_)
        print(rsp)



if __name__ == '__main__':
    main()
