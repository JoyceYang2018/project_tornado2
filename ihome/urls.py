#coding:utf-8

import os

from handlers import Passport,VerifyCode,House
from handlers.BaseHandler import StaticFileHandler

handlers=[
    (r'/api/imagecode',VerifyCode.ImageCodeHandler),
    (r'/api/smscode', VerifyCode.SMSCodeHandler),
    (r'/api/house/area$',House.AreaInfoHandler),
    (r'/api/house/my$',House.MyHouseHandler),
    (r'/(.*)',StaticFileHandler,dict(path=os.path.join(os.path.dirname(__file__),"html"),default_filename="index.html"))
]