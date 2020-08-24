from django.shortcuts import render, get_object_or_404
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from users.mixins import GuideRequiredMixin, BookingReviewCheckMixin, BookingCheckMixin, TourCheckMixin
from bookings.models import Booking, Feedback, Message
from tours.models import DayTour
from users.models import Guide
from django.contrib import messages

class Index(LoginRequiredMixin, GuideRequiredMixin, View):
    login_url = reverse_lazy('users:login')
    template_name = "guideadmin/index.html"
    def get(self, request, *args, **kwargs):
        bookings = request.user.guide.booking_set.order_by("-created_at")[:3]
        messages = Message.objects.filter(booking__guide=request.user.guide)[:3]
        context = { "bookings": bookings, "insite_mgs": messages}
        return render(self.request, self.template_name, context)

class BookingList(LoginRequiredMixin, GuideRequiredMixin, ListView):
    login_url = reverse_lazy('users:login')
    template_name = "guideadmin/booking-list.html"
    context_object_name = 'bookings'
    paginate_by = 5

    show_filter = False

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["bookings"] = context.get("page_obj")
        context["show_filter"] = self.show_filter
        return context

    def get_queryset(self):
        queryset = self.request.user.guide.booking_set
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

class BookingDetail(LoginRequiredMixin, GuideRequiredMixin, BookingCheckMixin, DetailView):
    model = Booking
    pk_url_kwarg = "booking_id"
    template_name = 'guideadmin/booking.html'


class FeedbackCreate(LoginRequiredMixin, GuideRequiredMixin, BookingReviewCheckMixin, CreateView):
    login_url = reverse_lazy('users:login')
    template_name = 'guideadmin/feedback.html'
    model = Feedback
    fields = ["feedback"]

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
        messages.info(self.request, "thank you for your feedback!")
        return reverse_lazy('guides:admin:booking_list') + "?status=finished"

class TourList(LoginRequiredMixin, GuideRequiredMixin, ListView):
    login_url = reverse_lazy('users:login')
    template_name = "guideadmin/tour-list.html"
    context_object_name = 'tours'
    paginate_by = 5

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["tours"] = context.get("page_obj")
        return context

    def get_queryset(self):
        queryset = self.request.user.guide.daytour_set.all()
        return queryset

class TourCreate(LoginRequiredMixin, GuideRequiredMixin, CreateView):
    login_url = reverse_lazy('users:login')
    template_name = 'guideadmin/tour.html'
    model = DayTour
    fields = ["name", "duration", "description", "tourtypes"]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_title"] = "Make your own tour"
        return context

    def form_valid(self, form):
        form.instance.by_guide = self.request.user.guide
        form.instance.region = self.request.user.guide.region
        form.instance.tour_price_without_tax = form.instance.get_tourprice_for_guide()
        form.instance.approved = False
        return super().form_valid(form)

    def get_success_url(self):
        messages.info(self.request, "Tour created!")
        return reverse_lazy('guides:admin:tour_list')

class TourEdit(LoginRequiredMixin, GuideRequiredMixin, TourCheckMixin, UpdateView):
    login_url = reverse_lazy('users:login')
    template_name = 'guideadmin/tour.html'
    model = DayTour
    pk_url_kwarg = "tour_id"
    fields = ["name", "duration", "description", "tourtypes"]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_title"] = "Edit tour"
        return context

    def form_valid(self, form):
        form.instance.tour_price_without_tax = form.instance.get_tourprice_for_guide()
        form.instance.approved = False
        return super().form_valid(form)

    def get_success_url(self):
        messages.info(self.request, "Tour updated!")
        return reverse_lazy('guides:admin:tour_list')

class ProfileEdit(LoginRequiredMixin, GuideRequiredMixin, UpdateView):
    login_url = reverse_lazy('users:login')
    template_name = 'guideadmin/profile.html'
    model = Guide
    fields = ['email', 'phone', 'has_national_license', 'region', 
              'name_jp', 'name_en', 'bank_name', 'bank_branch_number', 'bank_account_number', 'bank_username', ]

    def get_object(self):
        return self.request.user.guide

    def get_success_url(self):
        messages.info(self.request, "Profile updated!")
        return reverse_lazy('guides:admin:profile_edit')



