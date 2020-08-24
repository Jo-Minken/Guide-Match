from django.urls import path, include
from users.views_guideadmin import Index, BookingList, BookingDetail, FeedbackCreate, TourList, TourCreate, TourEdit, ProfileEdit

app_name = 'guides'

adminurlpatterns = [
    path('', Index.as_view(), name="index"),
    path('bookings', BookingList.as_view(), name="booking_list"),
    path('bookings/<int:booking_id>', BookingDetail.as_view(), name="booking"),
    path('bookings/<int:booking_id>/feedback', FeedbackCreate.as_view(), name="booking_feedback"),
    path('tours', TourList.as_view(), name="tour_list"),
    path('tours/create', TourCreate.as_view(), name="tour_create"),
    path('tours/<int:tour_id>/edit', TourEdit.as_view(), name="tour_edit"),
    path('profile-edit', ProfileEdit.as_view(), name="profile_edit"),
]

urlpatterns = [
    path('', include((adminurlpatterns, "guides"), namespace="admin")),
]