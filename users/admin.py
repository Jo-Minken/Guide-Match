from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from users.models import SiteUser, Guide

class MySiteUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ('Personal info', {'fields': ('user_type',)}),
    )

class MyGuideAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ('Personal info', {'fields': ('name_jp', 'name_en','user_type', 'phone', 'region', 'has_national_license')}),
        ('Bank info', {'fields': ('bank_name', 'bank_branch_number','bank_account_number', 'bank_username')}),
    )
    readonly_fields = ["bank_name", "bank_branch_number", "bank_account_number", "bank_username"]

admin.site.register(SiteUser, MySiteUserAdmin)
admin.site.register(Guide, MyGuideAdmin)