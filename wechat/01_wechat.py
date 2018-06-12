#coding:utf-8

import tornado.web
import tornado.options
import tornado.httpserver
import tornado.ioloop
import hashlib
import xmltodict
import time
import tornado.gen
import json
import os

from tornado.web import RequestHandler
from tornado.options import options,define
from tornado.httpclient import AsyncHTTPClient,HTTPRequest

WECHAT_TOKEN = 'yyz'
WECHAT_APP_ID = 'wxf311d1f06a329fad'
WECHAT_APP_SECRET = '224a0cf8bf2dbaef63f81f6ffde40eda'
define("port",default=8001,type=int,help="")

class AccessToken(object):
    #access_token辅助类
    _access_token = None
    _create_time = 0
    _expires_in = 0

    @classmethod
    @tornado.gen.coroutine
    def update_access_token(cls):
        client = AsyncHTTPClient()
        url = 'https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid=%s&secret=%s'%(WECHAT_APP_ID,WECHAT_APP_SECRET)
        resp = yield client.fetch(url)
        dict_data = json.loads(resp.body)
        if "errcode" in dict_data:
            raise Exception("wechat server error")
        else:
            cls._access_token=dict_data["access_token"]
            cls._expires_in = dict_data["expires_in"]
            cls._create_time = time.time()


    @classmethod
    @tornado.gen.coroutine
    def get_access_token(cls):
        if time.time()-cls._create_time>(cls._expires_in-200):
            #向微信服务器请求access_token
            yield cls.update_access_token()
            raise tornado.gen.Return(cls._access_token)
        else:
            raise tornado.gen.Return(cls._access_token)





class WechatHandler(RequestHandler):
    #对接微信服务器
    def prepare(self):
        signature = self.get_argument('signature')
        timestamp = self.get_argument('timestamp')
        nonce = self.get_argument('nonce')
        tmp = [WECHAT_TOKEN, timestamp, nonce]
        tmp.sort()
        tmp = ''.join(tmp)
        real_signature = hashlib.sha1(tmp.encode('utf-8')).hexdigest()
        if signature != real_signature:
            self.send_error(403)

    def get(self):
        echostr = self.get_argument('echostr')
        self.write(echostr)


    def post(self, *args, **kwargs):
        xml_data = self.request.body
        dict_data = xmltodict.parse(xml_data)
        msg_type = dict_data["xml"]["MsgType"]
        if msg_type == "text":
            content = dict_data["xml"]["Content"]
            resp_data = {
                "xml":{
                    "ToUserName":dict_data["xml"]["FromUserName"],
                    "FromUserName":dict_data["xml"]["ToUserName"],
                    "CreateTime":int(time.time()),
                    "MsgType":"text",
                    "Content":content,
                }
            }
            self.write(xmltodict.unparse(resp_data))

        elif msg_type == "event":
            if dict_data["xml"]["Event"] == "subscribe":
                #用户关注的事件
                resp_data = {
                    "xml": {
                        "ToUserName": dict_data["xml"]["FromUserName"],
                        "FromUserName": dict_data["xml"]["ToUserName"],
                        "CreateTime": int(time.time()),
                        "MsgType": "text",
                        "Content": u"您来啦，鸭鸭等你好久了～",
                    }
                }
                if "EventKey" in dict_data["xml"]:
                    event_key = dict_data["xml"]["EventKey"]
                    scene_id = event_key[8:]
                    resp_data["xml"]["Content"] = u"您来啦，鸭鸭等你%s次了～"%scene_id
                self.write(xmltodict.unparse(resp_data))
            elif dict_data["xml"]["Event"]=="SCAN":
                scene_id=dict_data["xml"]["EventKey"]
                resp_data = {
                    "xml": {
                        "ToUserName": dict_data["xml"]["FromUserName"],
                        "FromUserName": dict_data["xml"]["ToUserName"],
                        "CreateTime": int(time.time()),
                        "MsgType": "text",
                        "Content": u"您扫描的是%s"%scene_id,
                    }
                }
                self.write(xmltodict.unparse(resp_data))


        else:
            resp_data = {
                "xml":{
                    "ToUserName":dict_data["xml"]["FromUserName"],
                    "FromUserName":dict_data["xml"]["ToUserName"],
                    "CreateTime":int(time.time()),
                    "MsgType":"text",
                    "Content":"I love duck",
                }
            }
            self.write(xmltodict.unparse(resp_data))





class QrcodeHandler(RequestHandler):
    #请求微信服务器生成带参数二维码返回给客户
    @tornado.gen.coroutine
    def get(self, *args, **kwargs):
        scene_id = self.get_argument("sid")
        try:
            access_token=yield AccessToken.get_access_token()
        except Exception as e:
            self.write("errmsg:%s"%e)
        else:
            client=AsyncHTTPClient()
            url="https://api.weixin.qq.com/cgi-bin/qrcode/create?access_token=%s"%access_token
            req_data= {"action_name": "QR_LIMIT_SCENE", "action_info": {"scene": {"scene_id":scene_id}}}
            req = HTTPRequest(
                url=url,
                method="POST",
                body=json.dumps(req_data)
            )
            resp = yield client.fetch(req)
            dict_data=json.loads(resp.body)
            if "errcode" in dict_data:
                self.write("errmsg: get qrcode failed")
            else:
                ticket = dict_data["ticket"]
                qrcode_url = dict_data["url"]
                self.write('<img src="https://mp.weixin.qq.com/cgi-bin/showqrcode?ticket=%s"><br/>'%ticket)
                self.write('<p>%s</p>'%qrcode_url)


class ProfileHandler(RequestHandler):
    @tornado.gen.coroutine
    def get(self, *args, **kwargs):
        code = self.get_argument("code")
        client = AsyncHTTPClient()
        url="https://api.weixin.qq.com/sns/oauth2/access_token?appid=%s&secret=%s&code=%s&grant_type=authorization_code"%(WECHAT_APP_ID,WECHAT_APP_SECRET,code)
        resp=yield client.fetch(url)
        dict_data=json.loads(resp.body)
        if "errcode" in dict_data:
            self.write("error occur")
        else:
            access_token=dict_data["access_token"]
            open_id = dict_data["openid"]
            url = "https://api.weixin.qq.com/sns/userinfo?access_token=%s&openid=%s&lang=zh_CN"%(access_token,open_id)
            resp = yield client.fetch(url)
            user_data = json.loads(resp.body)
            if "errcode" in user_data:
                self.write("error occur again")
            else:
                self.render("index.html",user=user_data)



"""
用户最终访问的url
https://open.weixin.qq.com/connect/oauth2/authorize?appid=wxf311d1f06a329fad&redirect_uri=http%3A//www.idehai.com/wechat8001/profile&response_type=code&scope=snsapi_userinfo&state=1#wechat_redirect

"""





def main():
    tornado.options.parse_command_line()
    app=tornado.web.Application(
        [
            (r'/wechat8001',WechatHandler),
            (r'/qrcode',QrcodeHandler),
            (r'/wechat8001/profile',ProfileHandler),
        ],
        template_path=os.path.join(os.path.dirname(__file__),"template")
    )
    http_server = tornado.httpserver.HTTPServer(app)
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.current().start()

if __name__ == '__main__':
    main()