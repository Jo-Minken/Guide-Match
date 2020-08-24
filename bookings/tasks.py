from celery import task 
import datetime
from bookings.models import Booking

@task(name='mark_finished_tours') 
def mark_finished_tours():
    today = datetime.date.today()
    bookings = Booking.objects.filter(tourdate__lte= today, status="GuideMatched").all()
    
    for booking in bookings:
        booking.finished()
        booking.save()


# from celery.task.schedules import crontab
# from celery.decorators import periodic_task
# from celery import task

# import datetime
# from bookings.models import Booking
# from tours.models import TourType


# @periodic_task(run_every=(crontab(hour="17", minute="30")), name="run_at_17:30_daily", ignore_result=False)
# def mark_finished_tours():
#     today = datetime.date.today()
#     bookings = Booking.objects.filter(tourdate__lte= today, status="GuideMatched").all()
    
#     for booking in bookings:
#         booking.finished()
#         booking.save()
