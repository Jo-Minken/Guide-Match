from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from users.mixins import SiteUserRequiredMixin, BookingReviewCheckMixin, BookingCheckMixin, BookingCancelCheckMixin
from bookings.models import Booking, Review, Message
from users.models import SiteUser
from django.contrib import messages

class Index(LoginRequiredMixin, SiteUserRequiredMixin, View):
    login_url = reverse_lazy('users:login')
    template_name = "useradmin/index.html"
    def get(self, request, *args, **kwargs):
        bookings = request.user.siteuser.booking_set.order_by("-created_at")[:3]
        messages = Message.objects.filter(booking__customer=request.user.siteuser)[:3]
        context = { "bookings": bookings, "insite_mgs": messages}
        return render(self.request, self.template_name, context)

class BookingList(LoginRequiredMixin, SiteUserRequiredMixin, ListView):
    login_url = reverse_lazy('users:login')
    template_name = "useradmin/booking-list.html"
    context_object_name = 'bookings'
    paginate_by = 5

    show_filter = False

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["bookings"] = context.get("page_obj")
        context["show_filter"] = self.show_filter
        return context

    def get_queryset(self):
        queryset = self.request.user.siteuser.booking_set
        param_status = self.request.GET.get("status")

        if(param_status in ["upcoming", "finished", "cancelled"]):
          self.show_filter = True
        
        if(param_status == "upcoming"):
          queryset = queryset.filter(status__in=["New", "PaymentReceived", "PaymentFailed", "GuideMatched"])
        elif(param_status == "finished"):
          queryset = queryset.filter(status__in=["TourFinished", "SalaryPaid"])
        elif(param_status == "cancelled"):
          queryset = queryset.filter(status__in=["TourCanceled", "PaymentReturned"])


        queryset = queryset.extra(select={"booking_status":
                    "case when status = 'New' then 0 \
                          when status = 'PaymentReceived' then 1 \
                          when status = 'PaymentFailed' then 0 \
                          when status = 'GuideMatched' then 1 \
                          when status = 'TourFinished' then 5 \
                          when status = 'SalaryPaid' then 5 \
                          when status = 'PaymentReceived' then 4 \
                          when status = 'PaymentReturned' then 4 \
                          else 10 end"
                    }) \
                    .order_by('booking_status', 'tourdate', 'created_at')

        return queryset

class BookingDetail(LoginRequiredMixin, SiteUserRequiredMixin, BookingCheckMixin, DetailView):
    model = Booking
    pk_url_kwarg = "booking_id"
    template_name = 'useradmin/booking.html'

class ReviewCreate(LoginRequiredMixin, SiteUserRequiredMixin, BookingReviewCheckMixin, CreateView):
    login_url = reverse_lazy('users:login')
    template_name = 'useradmin/review.html'
    model = Review
    fields = ["score", "comment"]

    def dispatch(self, request, *args, **kwargs):
        self.booking = get_object_or_404(Booking, pk=kwargs.get('booking_id'))
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["booking"] = self.booking
        return context

    def form_valid(self, form):
        form.instance.booking = self.booking
        return super().form_valid(form)

    def get_success_url(self):
        messages.info(self.request, "the booking is reviewed!")
        return reverse_lazy('users:admin:booking_list') + "?status=finished"

class BookingCancel(LoginRequiredMixin, SiteUserRequiredMixin, BookingCancelCheckMixin, View):
    login_url = reverse_lazy('users:login')
    
    def post(self, request, *args, **kwargs):
        booking = get_object_or_404(Booking, pk=kwargs.get('booking_id'))
        booking.cancelled()
        booking.save()

        messages.info(request, "the booking is cancelled!")
        return HttpResponseRedirect(reverse_lazy('users:admin:booking_list') + "?status=cancelled")

class ProfileEdit(LoginRequiredMixin, SiteUserRequiredMixin, UpdateView):
    login_url = reverse_lazy('users:login')
    template_name = 'useradmin/profile.html'
    model = SiteUser
    fields = ['first_name', 'last_name', 'email', 'phone',]

    def get_object(self):
        return self.request.user.siteuser

    def get_success_url(self):
        messages.info(self.request, "Profile updated!")
        return reverse_lazy('users:admin:profile_edit')





