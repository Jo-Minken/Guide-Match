from django.db import models
from django.db.models import Sum
from django_fsm import FSMField, transition
from users.models import SiteUser, Guide, User
from tours.models import DayTour
from bookings.validators import validate_tourdate

from django.core.mail import send_mail
from guide_match.settings import EMAIL_HOST_USER

from datetime import date, datetime
from decimal import Decimal

class Booking(models.Model):
    tour = models.ForeignKey(DayTour, on_delete=models.CASCADE)
    guide = models.ForeignKey(Guide, on_delete=models.CASCADE, blank=True, null=True)
    customer = models.ForeignKey(SiteUser, on_delete=models.CASCADE)
    tourdate = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)

    BOOKING_STATUS = (
        'New', 
        'PaymentReceived', 
        'PaymentFailed', 
        'GuideMatched',
        'TourFinished', 
        'SalaryPaid',
        'TourCanceled',
        'PaymentReturned',
    )
    status = FSMField(default=BOOKING_STATUS[0], choices=zip(BOOKING_STATUS, BOOKING_STATUS))

    class Meta:
        unique_together = ('guide', 'tourdate',)
        
    def find_guide(self):
        if(self.tour.by_guide):
            tour_created_guide_available = Booking.objects \
                                    .filter(tourdate=self.tourdate, guide=self.tour.by_guide) \
                                    .count()

            if tour_created_guide_available == 0:
                return self.tour.by_guide

        region = self.tour.region
        unavailable_guides = Booking.objects \
                                    .filter(tourdate=self.tourdate, guide__isnull=False) \
                                    .values_list('guide', flat=True)
        guides = Guide.objects.filter(region=region)

        if(unavailable_guides.count() > 0):
            guides = guides.exclude(pk__in=list(unavailable_guides))

        guide = guides.order_by('?').first()
        return guide

    @staticmethod
    def get_format_date(param_date):
        return param_date.strftime("%d %b, %Y (%a)")

    def get_booking_date(self):
        return self.get_format_date(self.created_at)

    def get_tour_date(self):
        return self.get_format_date(self.tourdate)

    def get_cancelled_date(self):
        cancel_record = self.cancelrecord
        return self.get_format_date(cancel_record.created_at)

    def get_refunded_date(self):
        cancel_record = self.cancelrecord
        return self.get_format_date(cancel_record.refunded_at)

    def get_status_css_class(self):
        Status_CSS_Class = {
        'New':             'badge-primary', 
        'PaymentReceived': 'badge-success',
        'PaymentFailed':   'badge-warning',
        'GuideMatched':    'badge-info',
        'TourFinished':    'badge-light',
        'SalaryPaid':      'badge-success',
        'TourCanceled':    'badge-danger',
        'PaymentReturned': 'badge-danger',
        }
        return Status_CSS_Class.get(self.status)

    def get_status_for_user(self):
        Status = {
        'New':             'New Tour', 
        'PaymentReceived': 'Upcoming Tour',
        'PaymentFailed':   'Payment Failed',
        'GuideMatched':    'Upcoming Tour',
        'TourFinished':    'Finished Tour',
        'SalaryPaid':      'Finished Tour',
        'TourCanceled':    'Cancelled Tour',
        'PaymentReturned': 'Cancelled and Refunded',
        }
        return Status.get(self.status)

    def get_status_for_guide(self):
        Status = {
        'GuideMatched':    'Upcoming Tour',
        'TourFinished':    'Finished Tour',
        'SalaryPaid':      'Finished and Paid',
        'TourCanceled':    'Cancelled Tour',
        'PaymentReturned': 'Cancelled Tour',
        }
        return Status.get(self.status, "Upcoming Tour")

    def is_reviewable(self):
        return (self.status in ["TourFinished", "SalaryPaid"] and not hasattr(self, 'review') )

    def is_feedbackable(self):
        return (self.status in ["TourFinished", "SalaryPaid"] and not hasattr(self, 'feedback') )

    def is_cancellable(self):
        return self.status in ["New", "PaymentReceived", "PaymentFailed", "GuideMatched"]

    def is_cancelled(self):
        return self.status in ["TourCanceled", "PaymentReturned"]

    def get_cancellation_fee(self):
        day_interval = (self.tourdate - date.today()).days
        payment = self.payment_set.first()
        tour_fee = (payment and payment.amount) or 0

        cancellation_rate = 1

        if day_interval == 1:
            cancellation_rate = 0.6

        elif day_interval == 2:
            cancellation_rate = 0.5

        elif day_interval == 3:
            cancellation_rate = 0.4

        elif 3 < day_interval <= 7:
            cancellation_rate = 0.3

        elif 7 < day_interval <= 10:
            cancellation_rate = 0.2

        elif 10 < day_interval <= 14:
            cancellation_rate = 0.1

        elif 14 < day_interval:
            cancellation_rate = 0

        return '{:0.2f}'.format(tour_fee * Decimal(cancellation_rate))

    def is_salary_need_to_pay(self):
        return self.status == "TourFinished"

    def get_revenue(self):
        return self.payment_set.all().aggregate(revenue=Sum("amount")).get("revenue") or 0

    def get_guide_salary(self):
        revenue = self.get_revenue()
        guide_salary = revenue * 6 / 10
        return '{:0.2f}'.format(guide_salary)

    def get_refund(self):
        refund = self.get_revenue() - self.cancelrecord.cancellation_fee
        return '{:0.2f}'.format(refund)

    @transition(field=status, source='New', target='PaymentReceived')
    def pay(self, **kwargs):
        payment = Payment()
        payment.booking = self
        payment.payment_method = kwargs.get('payment_method', 1)
        payment.amount = self.tour.get_tax_in_price()

        payment.save()

    @transition(field=status, source='PaymentReceived', target='GuideMatched')
    def match_guide(self):
        return self.guide


    @transition(field=status, source='GuideMatched', target='TourFinished')
    def finished(self):
        subject = f"The tour {self.tour.name} is finished!"
        message_to_guide = "Please login to write tour feedback. Thank you!"
        message_to_user = "Please login to review the tour. Thank you!"
        guide_email = self.guide.email
        user_email = self.customer.email

        # send_mail(subject, message_to_guide, EMAIL_HOST_USER, [guide_email], fail_silently=True)
        # send_mail(subject, message_to_user, EMAIL_HOST_USER, [user_email], fail_silently=True)
        send_mail(subject, message_to_guide, EMAIL_HOST_USER, [EMAIL_HOST_USER])
        return True

    @transition(field=status, source='TourFinished', target='SalaryPaid')
    def pay_salary(self, created_by, note):
        transfer = SalaryTransfer()
        transfer.booking = self
        transfer.amount = self.get_guide_salary()
        transfer.note = note
        transfer.by_superuser = created_by

        transfer.save()

        subject = f"The tour {self.tour.name} is paid!"
        message_to_guide = "Please login to check the payment. Thank you!"
        guide_email = self.guide.email

        # send_mail(subject, message_to_guide, EMAIL_HOST_USER, [guide_email], fail_silently=True)
        return True

    @transition(field=status, source=["New", "PaymentReceived", "PaymentFailed", "GuideMatched"], target='TourCanceled')
    def cancelled(self):
        cancel_record = CancelRecord()
        cancel_record.booking = self
        cancel_record.cancellation_fee = self.get_cancellation_fee()
        
        cancel_record.save()

        # send mail to user guide and admin
        return True

    @transition(field=status, source='TourCanceled', target='PaymentReturned')
    def refund(self, created_by, note):
        cancel_record = self.cancelrecord
        cancel_record.is_refunded = True
        cancel_record.note = note
        cancel_record.refunded_at = datetime.now()
        cancel_record.by_superuser = created_by

        cancel_record.save()

        # send mail to user
        return True

    def __str__(self):
        return f"{self.id} - {self.tour.name} on {self.get_tour_date()}"


class Payment(models.Model):
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    
    PAYMENT_CHOICES = (
        (1, 'Credit card'),
    )
    payment_method = models.PositiveSmallIntegerField(choices=PAYMENT_CHOICES, null=False, default=1)
    amount = models.DecimalField(max_digits=5, decimal_places=2)

    def get_payment_method(self):
        return dict(self.PAYMENT_CHOICES).get(self.payment_method)


    def __str__(self):
        return f"Payment for booking id {self.booking.id}"

class SalaryTransfer(models.Model):
    booking = models.OneToOneField(Booking, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    amount = models.DecimalField(max_digits=5, decimal_places=2)
    note = models.TextField(null=True, blank=True)
    by_superuser = models.ForeignKey(User, on_delete=models.CASCADE)

class CancelRecord(models.Model):
    booking = models.OneToOneField(Booking, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    cancellation_fee = models.DecimalField(max_digits=5, decimal_places=2)
    is_refunded = models.BooleanField(default=False)
    refunded_at = models.DateTimeField(null=True, blank=True)
    note = models.TextField(null=True, blank=True)
    by_superuser = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)

class Review(models.Model):
    booking = models.OneToOneField(Booking, on_delete=models.CASCADE)
    SCORES = (
        (5, 'Excellent'),
        (4, 'Good'),
        (3, 'Not bad'),
        (2, 'Poor'),
        (1, 'Disappointing'),
    )
    score = models.PositiveSmallIntegerField(choices=SCORES, null=False, default=5)
    comment = models.TextField()

    def get_review_score(self):
        return dict(self.SCORES).get(self.score)

class Feedback(models.Model):
    booking = models.OneToOneField(Booking, on_delete=models.CASCADE)
    feedback = models.TextField()

class Message(models.Model):
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE)
    note = models.TextField(default="From Admin: ")
    created_at = models.DateTimeField(auto_now_add=True)

