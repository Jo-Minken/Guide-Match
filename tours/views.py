from django.views.generic import ListView, DetailView
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from tours.models import TourType, DayTour
from django.core.paginator import Paginator
from django.db.models import Count
from django.contrib import messages
import re

from tours.mixins import CheckApprovalMixin
# Create your views here.

class IndexList(ListView):

    context_object_name = 'daytours'
    queryset = DayTour.objects.filter(approved=True).all()[:6]
    template_name = 'index.html'

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        # Add in the tourtypes
        context["tourtypes"] = TourType.objects.annotate(tours_count=Count("daytour"))
        return context

class TourList(ListView):
    model = DayTour
    context_object_name = 'daytours'
    paginate_by = 10
    template_name = 'tour-list.html'
    tourtypes = TourType.objects.all()
    tourtype = None
    title_setting = { "show_region": False, "show_tourtype": False }

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        # Add in the tourtypes
        context["tourtypes"] = self.tourtypes
        context["tourtype"] = self.tourtype
        context["title_setting"] = self.title_setting
        context["day_tours"] = context.get("page_obj")
        return context
    
    def get_queryset(self):
        daytours = self.model.objects.filter(approved=True).all()
        param_region = self.request.GET.get("region")
        if param_region and param_region in ("Tokyo", "Kyoto", "Osaka"):
            daytours = daytours.filter(region = param_region)
            self.title_setting["show_region"] = True

        param_tourtype = self.request.GET.get("tourtype")
        if param_tourtype and re.match("\d+", param_tourtype):
            daytours = daytours.filter(tourtypes__id=param_tourtype)
            self.tourtype = self.tourtypes.filter(id=param_tourtype).first()
            self.title_setting["show_tourtype"] = True

        return daytours

class TourDetail(CheckApprovalMixin, DetailView):
    model = DayTour
    context_object_name = 'daytour'
    template_name = "tour-single.html"
    pk_url_kwarg = "tour_id"
    slug_url_kwarg = 'tour_slug'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        daytour = self.object
        context["more_tours"] = DayTour.objects.filter(region=daytour.region) \
                                .filter(tourtypes__id__in=daytour.tourtypes.all()) \
                                .filter(approved=True).order_by('?')[:3]
        return context

    def render_to_response(self, context):
        daytour = self.object
        tour_slug = self.kwargs.get("tour_slug", None)
        if not tour_slug:
            redirect_to = reverse('tours:tour_detail', kwargs={"tour_id": daytour.id, "tour_slug": daytour.slug})
            return HttpResponseRedirect(redirect_to)
        
        return super().render_to_response(context)
