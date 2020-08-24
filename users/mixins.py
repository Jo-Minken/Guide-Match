from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from django.contrib import messages
from bookings.models import Booking
from tours.models import DayTour
from django.shortcuts import get_object_or_404

class SiteUserRequiredMixin:

    def dispatch(self, request, *args, **kwargs):
        if request.user.user_type == 1:
            return super().dispatch(request, *args, **kwargs)
        else:
            messages.info(self.request, "only siteusers can access the user admin")
            return HttpResponseRedirect(reverse_lazy('users:login'))

class GuideRequiredMixin:

    def dispatch(self, request, *args, **kwargs):
        if request.user.user_type == 2:
            return super().dispatch(request, *args, **kwargs)
        else:
            messages.info(self.request, "only guides can access the guide admin")
            return HttpResponseRedirect(reverse_lazy('users:login'))

class BookingReviewCheckMixin:
    def dispatch(self, request, *args, **kwargs):
        booking = get_object_or_404(Booking, pk=kwargs.get('booking_id'))

        
        if request.user.user_type == 1:
            """
            booking check for site users
            """
            if booking.customer.pk == request.user.pk and booking.is_reviewable():
                return super().dispatch(request, *args, **kwargs)
            elif(not booking.is_reviewable()):
                messages.info(self.request, "the booking is not reviewable")
            else:
                messages.info(self.request, "the booking is not booked by you")
            
            return HttpResponseRedirect(request.META['HTTP_REFERER'])

        elif request.user.user_type == 2:
            """
            booking check for guides
            """
            if booking.guide.pk == request.user.pk and booking.is_feedbackable():
                return super().dispatch(request, *args, **kwargs)
            elif(not booking.is_feedbackable()):
                messages.info(self.request, "the booking is not feedbackable")
            else:
                messages.info(self.request, "the booking is not guided by you")
            
            return HttpResponseRedirect(request.META['HTTP_REFERER'])

        else:
            messages.info(self.request, "Booking check failed")
            return HttpResponseRedirect(request.META['HTTP_REFERER'])

class BookingCheckMixin:
    def dispatch(self, request, *args, **kwargs):
        booking = get_object_or_404(Booking, pk=kwargs.get('booking_id'))

        if request.user.user_type == 1:
            if booking.customer.pk == request.user.pk:
                return super().dispatch(request, *args, **kwargs)
            else:
                messages.info(self.request, "the booking is not booked by you")
            
            return HttpResponseRedirect(request.META['HTTP_REFERER'])

        elif request.user.user_type == 2:
            if booking.guide.pk == request.user.pk:
                return super().dispatch(request, *args, **kwargs)
            else:
                messages.info(self.request, "the booking is not guided by you")
            
            return HttpResponseRedirect(request.META['HTTP_REFERER'])

        else:
            messages.info(self.request, "Booking check failed")
            return HttpResponseRedirect(request.META['HTTP_REFERER'])

class BookingCancelCheckMixin:
    def dispatch(self, request, *args, **kwargs):
        booking = get_object_or_404(Booking, pk=kwargs.get('booking_id'))

        
        if request.user.user_type == 1:
            """
            booking check for site users
            """
            if booking.customer.pk == request.user.pk and booking.is_cancellable():
                return super().dispatch(request, *args, **kwargs)
            elif(not booking.is_cancellable()):
                messages.info(self.request, "the booking is not cancellable")
            else:
                messages.info(self.request, "the booking is not booked by you")
            
            return HttpResponseRedirect(request.META['HTTP_REFERER'])

        else:
            messages.info(self.request, "Booking check failed")
            return HttpResponseRedirect(request.META['HTTP_REFERER'])

class TourCheckMixin:
    def dispatch(self, request, *args, **kwargs):
        tour = get_object_or_404(DayTour, pk=kwargs.get('tour_id'))

        if tour.by_guide and tour.by_guide.pk == request.user.guide.pk:
            return super().dispatch(request, *args, **kwargs)
        else:
            messages.info(self.request, "the tour is not created by you")
            return HttpResponseRedirect(request.META.get('HTTP_REFERER', 
                                                     reverse_lazy('guides:admin:tour_list')))


            