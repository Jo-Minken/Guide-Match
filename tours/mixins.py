from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from django.contrib import messages
from django.shortcuts import get_object_or_404

class CheckApprovalMixin:

    def dispatch(self, request, *args, **kwargs):
        tour = self.get_object()
        if tour.approved:
            return super().dispatch(request, *args, **kwargs)
        else:
            messages.info(request, "Tour is not existed!")
            return HttpResponseRedirect(reverse_lazy('index'))