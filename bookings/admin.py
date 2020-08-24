from django.contrib import admin
from django.urls import reverse
from django.contrib.admin.templatetags.admin_urls import add_preserved_filters
from django.http import HttpResponseRedirect
from django.contrib import messages
from bookings.models import Booking, Payment, Review, Feedback, SalaryTransfer, CancelRecord, Message

class PaymentInline(admin.TabularInline):
    model = Payment
    extra = 0

class ReviewInline(admin.TabularInline):
    model = Review
    readonly_fields = ["booking", "score", "comment"]
    extra = 0
     
    def has_add_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

class FeedbackInline(admin.TabularInline):
    model = Feedback
    readonly_fields = ["booking", "feedback"]
    extra = 0

    def has_add_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

class SalaryTransferInline(admin.TabularInline):
    model = SalaryTransfer
    readonly_fields = ["booking", "created_at", "by_superuser"]
    extra = 0

    def has_add_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

class CancelRecordInline(admin.TabularInline):
    model = CancelRecord
    readonly_fields = ["booking", "created_at", "is_refunded", "refunded_at", "note", "by_superuser"]
    extra = 0

    def has_add_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

class MessageInline(admin.TabularInline):
    model = Message
    readonly_fields = ["booking", "created_at"]
    extra = 0

class BookingAdmin(admin.ModelAdmin):

    inlines = [PaymentInline, SalaryTransferInline, CancelRecordInline, ReviewInline, FeedbackInline, MessageInline]
    list_filter = ('status', )

    change_form_template = 'superadmin/change_form_template.html'

    def response_change(self, request, obj):
        opts = self.model._meta
        pk_value = obj._get_pk_val()
        preserved_filters = self.get_preserved_filters(request)

        if "_pay-salary" in request.POST and request.user.user_type == 0:
            transfer_note = request.POST.get("_note")
            obj.pay_salary(request.user, transfer_note)
            obj.save()

            redirect_url = reverse('admin:%s_%s_change' % (opts.app_label, opts.model_name),
                                    args=(pk_value,),
                                    current_app=self.admin_site.name)
            redirect_url = add_preserved_filters({'preserved_filters': preserved_filters, 'opts': opts}, redirect_url)

            messages.info(request, "Salary transfered!")
            return HttpResponseRedirect(redirect_url)

        elif "_refund" in request.POST and request.user.user_type == 0:
            transfer_note = request.POST.get("_note")
            obj.refund(request.user, transfer_note)
            obj.save()

            redirect_url = reverse('admin:%s_%s_change' % (opts.app_label, opts.model_name),
                                    args=(pk_value,),
                                    current_app=self.admin_site.name)
            redirect_url = add_preserved_filters({'preserved_filters': preserved_filters, 'opts': opts}, redirect_url)

            messages.info(request, "Payment refunded!")
            return HttpResponseRedirect(redirect_url)
        else:
            return super(BookingAdmin, self).response_change(request, obj)

admin.site.register(Booking, BookingAdmin)