from django.urls import path, re_path
from tours.views import TourList, TourDetail

app_name = 'tours'
urlpatterns = [
    path('', TourList.as_view(), name="tour_list"),
    re_path(r'^(?P<tour_id>\d+)/(?:(?P<tour_slug>[\w\-]+)/)?$', TourDetail.as_view(), name="tour_detail"),
]