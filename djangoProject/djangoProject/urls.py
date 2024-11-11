# NosqlWork/urls.py
from django.contrib import admin
from django.urls import path, include
from hotel import utils
from hotel.views import *

urlpatterns = [
    path('admin/', admin.site.urls),
    path('test/importData/', import_data_view, name='import_data'),  # 添加路径和视图
    path('', index, name='index'),
    path('api/getScores/', get_scores_view, name='get_scores_view'),
    path('api/getScorePriceRelationship/', get_score_price_relationship_view, name='get_score_price_relationship_view'),
    path('api/getHotelHeatMap/', get_hotel_heat_map_view, name='get_hotel_heat_map_view'),
    path('api/getCount/', get_count_view, name='get_count_view'),
    path('api/getHighScoreComment/', get_high_score_comment_view, name='get_high_score_comment_view'),
    path('api/getRoomDetail/', get_room_detail_view, name='get_room_detail_view'),
    path('api/getCountByType/', get_count_by_type_view, name='get_count_by_type_view'),
]
