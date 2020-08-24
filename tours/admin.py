from django.contrib import admin
from tours.models import TourType, DayTour

class TourAdmin(admin.ModelAdmin):

    list_filter = ('approved', )

# Register your models here.
admin.site.register(TourType)
admin.site.register(DayTour, TourAdmin)