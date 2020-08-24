from django.urls import path
from users.views_useradmin import Index, BookingList, BookingDetail, ReviewCreate, BookingCancel, ProfileEdit

app_name = 'users'

urlpatterns = [
    path('', Index.as_view(), name="index"),
    path('bookings', BookingList.as_view(), name="booking_list"),
    path('bookings/<int:booking_id>', BookingDetail.as_view(), name="booking"),
    path('bookings/<int:booking_id>/review', ReviewCreate.as_view(), name="booking_review"),
    path('bookings/<int:booking_id>/cancel', BookingCancel.as_view(), name="booking_cancel"),
    path('profile-edit', ProfileEdit.as_view(), name="profile_edit"),
]