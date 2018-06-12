#coding:utf-8

from .BaseHandler import BaseHandler

class IndexHandler(BaseHandler):
    def get(self):
        # self.application.db
        # self.application.redis
        self.write("hello world")