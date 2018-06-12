#coding:utf-8

import logging
import constants
import json

from .BaseHandler import BaseHandler
from utils.response_code import RET
from utils.common import require_logined

class AreaInfoHandler(BaseHandler):
    def get(self):
        try:
            ret=self.redis.get("area_info")#get取的字符串类型
        except Exception as e:
            logging.error(e)
            ret = None
        if ret:
            logging.debug(ret)
            logging.info("hit redis cache")
            #直接拼接成json，这样就不用dumps，序列化和反序列化操作费时占内存
            return self.write('{"errno":%s,"errmsg":"ok","data":%S}'%(RET.OK,ret))
        try:
            ret = self.db.query("select ai_area_id,ai_name from ih_area_info")
        except Exception as e:
            logging.error(e)
            return self.write(dict(errno=RET.DBERR,errmsg="get data error"))
        if not ret:
            return self.write(dict(errno=RET.NODATA,errmsg="no area data"))
        areas = []
        for l in ret:
            area={
                "area_id":l["ai_area_id"],
                "name":l["ai_name"]
            }
            areas.append(area)
        try:
            self.redis.setex("area_info",constants.REDIS_AREA_INFO_EXPIRES_SECONDES,json.dumps(areas))
        except Exception as e:
            logging.error(e)

        self.write(dict(errno=RET.OK,errmsg="ok",data=areas))


class MyHouseHandler(BaseHandler):
    @require_logined
    #装饰器中出发了get_current_user方法，已经用了self.session方法把self存到了session里面
    def get(self):
        user_id = self.session.data["user_id"]
        try:
            ret = self.db.query("select a.hi_house_id,a.hi_title,a.hi_price,a.hi_ctime,b.ai_name,a.hi_index_image_url from ih_house_info a inner join ih_area_info b on a.hi_area_id=b.ai_area_id where a.hi_user_id=%s;",user_id)#不用%代换，会有注入攻击
        except Exception as e:
            logging.error(e)
            return self.write({"errcode": RET.DBERR, "errmsg": "get data erro"})
        houses = []
        if ret:
            for l in ret:
                house = {
                    "house_id": l["hi_house_id"],
                    "title": l["hi_title"],
                    "price": l["hi_price"],
                    "ctime": l["hi_ctime"].strftime("%Y-%m-%d"),  # 将返回的Datatime类型格式化为字符串
                    "area_name": l["ai_name"],
                    "img_url": constants.QINIU_URL_PREFIX + l["hi_index_image_url"] if l["hi_index_image_url"] else ""
                }
                houses.append(house)
        self.write({"errcode": RET.OK, "errmsg": "OK", "houses": houses})


