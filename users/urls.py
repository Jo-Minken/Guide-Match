from django.urls import path, include
from users.views import UserSignUp, UserLogOut, UserLogIn, GuideSignUp
import users.views as users_view

app_name = 'users'
urlpatterns = [
    path('register/', UserSignUp.as_view(), name="register"),
    path('guide-register/', GuideSignUp.as_view(), name="guide_register"),
    path('logout/', UserLogOut.as_view(), name="logout"),
    path('login/', UserLogIn.as_view(), name="login"),

    path('bookings/<int:booking_id>/message_create', users_view.message_create, name="message_create"),

    path('', include('users.urls_useradmin', namespace="admin")),
]