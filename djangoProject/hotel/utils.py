from traceback import print_tb

import pandas as pd
import requests

from .models import HotelInfo, HotelRoom, RoomMapping, LocationEmbedded


def import_hotel_data(excel_file):
    # 读取Excel文件
    df = pd.read_excel(excel_file)
    # 定义映射关系
    grade_mapping = {
        '三星级': 3,
        '四星级': 4,
        '五星级': 5,
        '高档型': 11,
        '豪华型': 12,
        '经济型': 13,
        '舒适型': 14
    }
    comment_mapping = {
        '好': 1,
        '很好': 2,
        '不错': 3,
        '棒': 4,
        '超棒': 5
    }

    # 遍历DataFrame中的每一行，导入数据
    for _, row in df.iterrows():
        hotel_info = HotelInfo(
            _id=row['id'],
            hotel_name=str(row['hotel_name']),
            hotel_id=str(row['hotel_id']),
            hotel_score=row['hotel_score'],
            hotel_image_id=str(row['hotel_image_id']),
            # hotel_location_info=str(row['hotel_location_info']),
            hotel_grade_text=grade_mapping.get(row['hotel_grade_text'], None),
            hotel_comment_desc=comment_mapping.get(row['hotel_comment_desc'], None),
            # hotel_city_name=str(row['hotel_city_name'])
            hotel_location=LocationEmbedded(hotel_city_name=str(row['hotel_city_name']),
                                            hotel_location_info=str(row['hotel_location_info'])
                                            ),
        )
        hotel_info.save()


def import_room_data(excel_file):
    df = pd.read_excel(excel_file)

    data_mapping = {
        '有wifi': 1,
        '无wifi': 0
    }

    for _, row in df.iterrows():
        hotel_room = HotelRoom(
            _id=row['id'],
            # room_name=str(row['room_name']),
            hotel_id=str(row['hotel_id']),
            room_id=str(row['room_id']),
            # room_image_url=str(row['room_image_url']),
            room_area=str(row['room_area']).replace('㎡', '').strip(),
            room_bed_type=str(row['room_bed_type']),
            room_window=str(row['room_window']),
            room_breakfast_num=str(row['room_breakfast_num']),
            room_wifi=data_mapping.get(row['room_wifi'], None),
            room_price=row['room_price'],
            room_exist_num=str(row['room_exist_num'])
        )
        hotel_room.save()
        room_mapping = RoomMapping(
            _id=str(row['room_id']),
            name=str(row['room_name']),
            image_url=str(row['room_image_url'])
        )
        room_mapping.save()


def import_all_data():
    hotel_data_path = "./excels/hotel_info.xlsx"
    hotel_room_path = "./excels/hotel_room.xlsx"
    import_hotel_data(hotel_data_path)
    import_room_data(hotel_room_path)
    print('数据导入成功')


def get_district_from_address_baidu(address, city):
    ak = "RrKFesYlIOoTd4BPD4vBDxkfOtffUZk2"  # 替换成你申请的百度地图API密钥
    url = f"http://api.map.baidu.com/geocoding/v3/?ak={ak}&address={address}&city={city}&output=json"

    response = requests.get(url)
    result = response.json()

    if result['status'] == 0:
        return_info = {'jd': result['result']['location']['lng'], 'wd': result['result']['location']['lat']}
        return return_info  # 返回所在区域的经纬度
    else:
        return None


def get_district_from_address_gaode(address):
    # 替换成你自己的高德地图API密钥
    api_key = "256fdd83c65201c34ce44385a8b32ae0"
    # 构造请求 URL
    url = f"https://restapi.amap.com/v3/geocode/geo?key={api_key}&address={address}"

    response = requests.get(url)
    result = response.json()

    # 判断请求是否成功
    if result['status'] == '1' and result['geocodes']:
        # 获取返回的地理编码结果
        location_info = str(result['geocodes'][0]['location']).split(',')
        return_info = {'wd': location_info[0], 'jd': location_info[1]}
        return return_info
    else:
        return None
