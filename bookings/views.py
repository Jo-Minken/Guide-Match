from django.shortcuts import render, get_object_or_404
from django.views.generic import CreateView
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from django.contrib import messages

from bookings.forms import PaymentForm
from bookings.models import Booking
from tours.models import DayTour

class PayView(LoginRequiredMixin, View):
    login_url = reverse_lazy('users:login')
    template_name = 'payment.html'
    success_message = 'Your booking has been created'
    success_url = reverse_lazy('index')

    def get(self, request, *args, **kwargs):
        tour_id = kwargs.get("tour_id")
        tour = get_object_or_404(DayTour, id=tour_id)
        tourdate = request.GET.get("tourdate")

        form = PaymentForm({"payment_method":1, "tourdate": tourdate})
        context = {"form": form, "tour": tour, "tourdate": tourdate, }
        return render(self.request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        post_params = request.POST
        user = request.user
        form = PaymentForm(post_params)

        if form.is_valid():
            booking = Booking()
            booking.customer = request.user.siteuser

            tour_id = kwargs.get("tour_id")
            tour = get_object_or_404(DayTour, id=tour_id)

            booking.tour = tour
            booking.tourdate = form.cleaned_data['tourdate']
            booking.guide = booking.find_guide()
            booking.save()

            booking.pay(payment_method=form.cleaned_data['payment_method'])
            booking.save()

            booking.match_guide()
            booking.save()

            messages.info(self.request, f"{ user.username }, {self.success_message}")
            return HttpResponseRedirect(self.success_url)
        else:
            context = {"form": form, }
            return render(self.request, self.template_name, context)
