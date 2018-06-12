#coding:utf-8

import functools

from utils.response_code import RET

def require_logined(fun):
    @functools.wraps(fun)
    def wrapper(request_handler_obj,*args,**kwargs):
        #如果返回的不是一个空字典，证明用户已经登陆过，保存了用户的session数据
        if not request_handler_obj.get_current_user:
            fun(request_handler_obj,*args,**kwargs)
        else:
            request_handler_obj.write(dict=(errno=RET.SESSIONERR,errmsg="用户未登录"))
    return wrapper