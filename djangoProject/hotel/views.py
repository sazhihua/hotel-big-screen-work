import time
from re import search

from django.shortcuts import render
from django.http import HttpResponse, JsonResponse

from .models import HotelInfo
from .utils import *
import statistics
from mongoengine import Q
import requests


def import_data_view(request):
    if request.method == 'POST':
        import_all_data()  # 调用导入函数
        return HttpResponse("数据导入成功！")
    return render(request, 'import_data.html')  # 渲染上传文件的页面


def index(request):
    return render(request, 'index.html')


# 展示酒店评分的平均分、中位数、最高分、最低分、众数，以数据集中“hotel_score”属性为依据进行展示；
def get_scores_view(request):
    # hotel_score = HotelInfo.objects(hotel_score__ne=float('nan')).only('hotel_score')
    hotel_score = HotelInfo.objects(Q(hotel_score__ne=None)).only('hotel_score')
    hotel_score_jjx = HotelInfo.objects(Q(hotel_score__ne=None) & Q(hotel_grade_text=13)).only('hotel_score')
    hotel_score_gdx = HotelInfo.objects(Q(hotel_score__ne=None) & Q(hotel_grade_text=12)).only('hotel_score')
    hotel_score = [x.hotel_score for x in hotel_score]
    hotel_score_jjx = [x.hotel_score for x in hotel_score_jjx]
    hotel_score_gdx = [x.hotel_score for x in hotel_score_gdx]
    return JsonResponse(data={
        'data': True,
        'zt': {'average': round(statistics.mean(hotel_score), 2), 'median': statistics.median(hotel_score),
               'max': max(hotel_score), 'min': min(hotel_score), 'mode': statistics.mode(hotel_score)},
        'jjx': {'average': round(statistics.mean(hotel_score_jjx), 2), 'median': statistics.median(hotel_score_jjx),
                'max': max(hotel_score_jjx), 'min': min(hotel_score_jjx), 'mode': statistics.mode(hotel_score_jjx)},
        'gdx': {'average': round(statistics.mean(hotel_score_gdx), 2), 'median': statistics.median(hotel_score_gdx),
                'max': max(hotel_score_gdx), 'min': min(hotel_score_gdx), 'mode': statistics.mode(hotel_score_gdx)}
    })


def get_score_price_relationship_view(request):
    query_type = int(request.GET.get('option'))
    if query_type == 0:
        # 执行聚合查询
        pipeline = [
            {
                '$lookup': {
                    'from': 'hotel_room',  # 目标集合的名称
                    'localField': 'hotel_id',
                    'foreignField': 'hotel_id',
                    'as': 'rooms'
                }
            },
            {
                '$unwind': {
                    'path': '$rooms',
                    'preserveNullAndEmptyArrays': True  # 可选，保留没有房间的酒店
                }
            },
            {
                '$group': {
                    '_id': '$hotel_id',
                    'hotel_grade_text': {'$first': '$hotel_grade_text'},
                    'hotel_score': {'$first': '$hotel_score'},
                    'max_room_price': {'$max': '$rooms.room_price'}
                }
            },
            {
                '$match': {
                    'hotel_grade_text': {'$ne': None},
                    'hotel_score': {'$ne': None},
                    'max_room_price': {'$ne': None},  # 只保留 max_room_price 不为空的记录
                }
            },
            {
                '$project': {
                    '_id': 0,
                    'hotel_id': '$_id',
                    'hotel_score': 1,
                    'max_room_price': 1
                }
            }
        ]
    else:
        # 执行聚合查询
        pipeline = [
            {
                '$lookup': {
                    'from': 'hotel_room',  # 目标集合的名称
                    'localField': 'hotel_id',
                    'foreignField': 'hotel_id',
                    'as': 'rooms'
                }
            },
            {
                '$unwind': {
                    'path': '$rooms',
                    'preserveNullAndEmptyArrays': True  # 可选，保留没有房间的酒店
                }
            },
            {
                '$group': {
                    '_id': '$hotel_id',
                    'hotel_grade_text': {'$first': '$hotel_grade_text'},
                    'hotel_score': {'$first': '$hotel_score'},
                    'max_room_price': {'$max': '$rooms.room_price'}
                }
            },
            {
                '$match': {
                    'hotel_grade_text': {'$ne': None, '$eq': query_type},
                    'hotel_score': {'$ne': None},
                    'max_room_price': {'$ne': None},  # 只保留 max_room_price 不为空的记录
                }
            },
            {
                '$project': {
                    '_id': 0,
                    'hotel_id': '$_id',
                    'hotel_score': 1,
                    'max_room_price': 1
                }
            }
        ]

    # 使用 aggregate 方法执行聚合查询
    results = list(HotelInfo.objects.aggregate(pipeline))

    return JsonResponse({'data': results})


def get_hotel_heat_map_view(request):
    global hotel_infos
    results = []
    query_city = request.GET.get('mapName')
    if query_city == 'china':
        pipeline = [
            {
                "$group": {
                    "_id": "$hotel_city_name",  # 按照 hotel_city_name 字段分组
                    "count": {"$sum": 1}  # 统计每个城市的数量
                }
            },
            {
                "$sort": {"count": -1}  # 按照 count 字段降序排序
            }
        ]
        # 执行聚合操作
        results = list(HotelInfo.objects.aggregate(*pipeline))
        return JsonResponse({'data': results})
    elif query_city == 'beijing':
        hotel_infos = HotelInfo.objects(hotel_grade_text=11, hotel_city_name='北京').only('hotel_location_info',
                                                                                          'hotel_city_name',
                                                                                          'hotel_name')
    elif query_city == 'tianjin':
        hotel_infos = HotelInfo.objects(hotel_grade_text=11, hotel_city_name='天津').only('hotel_location_info',
                                                                                          'hotel_city_name',
                                                                                          'hotel_name')
    elif query_city == 'mix':
        hotel_infos = HotelInfo.objects(hotel_grade_text=11, hotel_city_name__in=['天津', '北京']).only(
            'hotel_location_info',
            'hotel_city_name',
            'hotel_name')
    # for hotel_info in hotel_infos:
    #     address = hotel_info.hotel_city_name + hotel_info.hotel_name + hotel_info.hotel_location_info
    #     lng_lat_info = get_district_from_address_gaode(address)
    #     if lng_lat_info is not None:
    #         results.append(lng_lat_info)
    #         time.sleep(1 / 3)
    for hotel_info in hotel_infos:
        address = hotel_info.hotel_city_name + hotel_info.hotel_name + hotel_info.hotel_location_info
        lng_lat_info = get_district_from_address_baidu(address)
        if lng_lat_info is not None:
            results.append(lng_lat_info)
            time.sleep(1 / 30)
    return JsonResponse({'data': results})


def get_count_view(request):
    syjds = len(HotelInfo.objects().only('_id'))
    gdjds = len(HotelInfo.objects(hotel_grade_text=11).only('_id'))
    gfjds = len(HotelInfo.objects(hotel_score__gte=4.5).only('_id'))
    dfjds = len(HotelInfo.objects(hotel_score__lt=4.0).only('_id'))
    return JsonResponse({'data': True, 'syjds': syjds, 'gdjds': gdjds, 'gfjds': gfjds, 'dfjds': dfjds})


def get_high_score_comment_view(request):
    # 获取前10个评分最高的酒店，使用 only() 优化查询字段
    top_hotels = HotelInfo.objects.only("hotel_name", "hotel_image_id", "hotel_comment_desc") \
                     .order_by("-hotel_score")[:10]

    # 手动将 QuerySet 转换为字典列表
    top_hotels_list = [{
        'hotel_name': hotel.hotel_name,
        'hotel_image_id': hotel.hotel_image_id,
        'hotel_comment_desc': hotel.hotel_comment_desc
    } for hotel in top_hotels]

    # 返回 JSON 响应
    return JsonResponse({'data': top_hotels_list})


def get_room_detail_view(request):
    search_hotel_city = request.GET.get('roomCity')
    search_hotel_name = request.GET.get('roomName')

    # 假设传入的 data 是查询条件
    hotel_info = HotelInfo.objects(hotel_name__regex=search_hotel_name, hotel_city_name=search_hotel_city).first()

    # 获取到 hotel_id
    hotel_id = hotel_info.hotel_id if hotel_info else None

    if hotel_id:
        # MongoDB 聚合查询管道
        pipeline = [
            {
                '$match': {'hotel_id': hotel_id}
            },
            {
                '$lookup': {
                    'from': 'room_mapping',
                    'localField': 'room_id',
                    'foreignField': '_id',
                    'as': 'room_details'
                }
            },
            {
                '$unwind': {
                    'path': '$room_details',
                    'preserveNullAndEmptyArrays': True
                }
            },
            {
                '$project': {
                    'room_id': 1,
                    'room_price': 1,
                    'room_area': 1,
                    'room_name': '$room_details.name',
                    'room_image_url': '$room_details.image_url',
                    'room_bed_type': 1,
                    'room_exist_num': 1,
                    'room_breakfast_num': 1,
                    'room_window': 1,
                    'room_wifi': 1
                }
            }
        ]

        # 执行聚合查询
        results = list(HotelRoom.objects.aggregate(*pipeline))

    else:
        hotel_rooms = []
        results = []

    # 返回 JSON 响应
    return JsonResponse({'data': results})


def get_count_by_type_view(request):
    if request.GET.get('var1') and request.GET.get('var2'):
        pipeline = [
            {
                '$match': {  # 过滤掉 hotel_grade_text 为 null 或者为空字符串的记录
                    'hotel_grade_text': {'$ne': None},
                    'hotel_city_name': {'$eq': request.GET.get('var1')}
                }
            },
            {
                '$group': {  # 按照 hotel_grade_text 分组
                    '_id': '$hotel_grade_text',  # 以 hotel_grade_text 为分组依据
                    'count': {'$sum': 1}  # 统计每个分组的数量
                }
            },
            {
                '$sort': {  # 可选：按分类名称排序
                    'hotel_grade_text': -1  # 或者 -1，决定升序或降序
                }
            }
        ]
        # 执行聚合查询并转换为 List
        results1 = list(HotelInfo.objects.aggregate(*pipeline))
        pipeline = [
            {
                '$match': {  # 过滤掉 hotel_grade_text 为 null 或者为空字符串的记录
                    'hotel_grade_text': {'$ne': None},
                    'hotel_city_name': {'$eq': request.GET.get('var2')}
                }
            },
            {
                '$group': {  # 按照 hotel_grade_text 分组
                    '_id': '$hotel_grade_text',  # 以 hotel_grade_text 为分组依据
                    'count': {'$sum': 1}  # 统计每个分组的数量
                }
            },
            {
                '$sort': {  # 可选：按分类名称排序
                    'hotel_grade_text': -1  # 或者 -1，决定升序或降序
                }
            }
        ]
        results2 = list(HotelInfo.objects.aggregate(*pipeline))
        return JsonResponse({'data': True, 'results1': results1, 'results2': results2})
    else:
        pipeline = [
            {
                '$match': {
                    'hotel_grade_text': {'$ne': None}
                }
            },
            {
                '$group': {
                    '_id': '$hotel_grade_text',  # 以 hotel_grade_text 为分组依据
                    'count': {'$sum': 1}
                }
            },
            {
                '$sort': {
                    'count': -1
                }
            }
        ]

        # 执行聚合查询并转换为 List
        results = list(HotelInfo.objects.aggregate(*pipeline))
        return JsonResponse({'data': results})
