from django.urls import path
from bookings.views import PayView

app_name = 'bookings'
urlpatterns = [
    path('<int:tour_id>/payment', PayView.as_view(), name="payment"),
]