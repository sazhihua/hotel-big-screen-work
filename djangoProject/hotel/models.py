from mongoengine import Document, StringField, FloatField, IntField, EmbeddedDocument, EmbeddedDocumentField
from django.db import models


class LocationEmbedded(EmbeddedDocument):
    hotel_location_info = StringField(max_length=1000, blank=True)  # 酒店位置描述
    hotel_city_name = StringField(max_length=100, blank=True)  # 酒店城市名称


# 6600条数据
class HotelInfo(Document):
    _id = IntField(primary_key=True)  # 自定义主键，类型为整型
    hotel_name = StringField(max_length=255, blank=True)  # 酒店名称
    hotel_id = StringField(max_length=100, blank=True)  # 酒店 ID
    hotel_score = FloatField(blank=True)  # 酒店评分
    hotel_image_id = StringField(max_length=255, blank=True)  # 酒店图片 ID
    # hotel_location_info = StringField(max_length=1000, blank=True)  # 酒店位置描述
    hotel_grade_text = IntField(blank=True)  # 3三星级，4四星级，5五星级，11高档型，12豪华型，13经济型，14舒适型
    hotel_comment_desc = IntField(blank=True)  # 1好，2很好，3不错，4棒，5超棒
    # hotel_city_name = StringField(max_length=100, blank=True)  # 酒店城市名称
    hotel_location = EmbeddedDocumentField(LocationEmbedded)  # 嵌套文档

    def __str__(self):
        return self.hotel_name


# 135788条数据
class HotelRoom(Document):
    _id = IntField(primary_key=True)  # 自定义主键，类型为整型
    # room_name = StringField(max_length=255, blank=True)  # 房间名称
    hotel_id = StringField(max_length=100, blank=True)  # 酒店 ID
    room_id = StringField(max_length=100, blank=True)  # 房间 ID
    # room_image_url = StringField(max_length=255, blank=True)  # 房间图片 ID
    room_area = StringField(max_length=100, blank=True)  # 房间面积，不保存单位m^2
    room_bed_type = StringField(max_length=100, blank=True)  # 床型
    room_window = StringField(max_length=255, blank=True)  # 窗户信息
    room_breakfast_num = StringField(max_length=255, blank=True)  # 早餐数量
    room_wifi = IntField(blank=True)  # 1表示有wifi，0表示无wifi
    room_price = IntField(required=True, blank=True)  # 房间价格
    room_exist_num = StringField(max_length=100, blank=True)  # 房间数量

    def __str__(self):
        return self.room_id


class RoomMapping(Document):
    _id = StringField(primary_key=True)  # 房间 ID
    name = StringField(max_length=255, blank=True)  # 房间名称
    image_url = StringField(max_length=255, blank=True)

    def __str__(self):
        return self.name
