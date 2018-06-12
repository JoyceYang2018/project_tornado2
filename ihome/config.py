#coding:utf-8

import os

# Application配置参数
settings = {
    "static_path":os.path.join(os.path.dirname(__file__),"static"),
    "template_path":os.path.join(os.path.dirname(__file__),"template"),
    "cookie_secret":"jfNgg9XxRC+O8FFsFLJUgyzRF9M30ELwinMUWLO3w7c=",
    "XSRF_Cookies":True,
    "debug": True,
}

#mysql
mysql_options=dict(
    host = "127.0.0.1",
    database = "ihome",
    user = "root",
    password = "66666666",
)

#redis
redis_options=dict(
    host = "127.0.0.1",
    port = 6379
)

log_file = os.path.join(os.path.dirname(__file__),"logs/log")
log_level = "debug"
session_expires = 86400 # session数据有效期， 单位秒