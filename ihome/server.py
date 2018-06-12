# coding:utf-8

import tornado.web
import tornado.ioloop
import tornado.options
import tornado.httpserver
import config
import torndb
import redis

from tornado.options import define,options
from tornado.web import RequestHandler
from urls import handlers

define("port",type=int,default=8000,help="run server on the given port")

class Application(tornado.web.Application):
    #重写Application类，在创建app实例的时候就初始化连接数据库
    def __init__(self,*args,**kwargs):
        super(Application,self).__init__(*args,**kwargs)
        # self.db = torndb.Connection(
        #     host=config.mysql_options["host"],
        #     database=config.mysql_options["database"],
        #     user=config.mysql_options["user"],
        #     password=config.mysql_options["password"],
        # )
        #可以用××来解包
        self.db = torndb.Connection(**config.mysql_options)
        # self.redis = redis.StrictRedis(
        #     host=config.redis_options["host"],
        #     port=config.redis_options["port"]
        # )
        self.redis = redis.StrictRedis(**config.redis_options)


def main():
    options.log_file_prefix = config.log_file
    options.logging = config.log_level
    tornado.options.parse_command_line()
    app = Application(
        handlers, **config.settings
    )
    http_server = tornado.httpserver.HTTPServer(app)
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.current().start()

if __name__=='__main__':
    main()