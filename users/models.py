from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.urls import reverse_lazy

class User(AbstractUser):
    USER_TYPE_CHOICES = (
        (0, 'admin'),
        (1, 'user'),
        (2, 'guide'),
    )
    
    user_type = models.PositiveSmallIntegerField(choices=USER_TYPE_CHOICES, null=False, default=0)
    
    def get_admin_url(self):
        if self.user_type == 0:
            return reverse_lazy("admin:index")

        elif self.user_type == 1:
            return reverse_lazy("users:admin:index")

        elif self.user_type == 2:
            return reverse_lazy("guides:admin:index")

        else:
            return reverse_lazy("index")

    def __str__(self):
        return self.username

class SiteUser(User):
    phone = models.CharField(max_length=30)
    
    class Meta:
        verbose_name = _('siteuser')
        verbose_name_plural = _('siteusers')

    def save(self, *args, **kwargs):
        self.user_type = 1
        super().save(*args, **kwargs)

    def __str__(self):
        return self.username
  
class Guide(User):

    REGION_CHOICES = (
        ('Tokyo'),
        ('Osaka'),
        ('Kyoto'),
    )

    has_national_license = models.BooleanField(default=False)
    phone = models.CharField(max_length=30)
    region = models.CharField(choices=zip(REGION_CHOICES, REGION_CHOICES), max_length=30, default="Tokyo")
    name_jp = models.CharField(max_length=10)
    name_en = models.CharField(max_length=50)

    bank_name = models.CharField(max_length=50, null=True, blank=True)
    bank_branch_number = models.CharField(max_length=10, null=True, blank=True)
    bank_account_number = models.CharField(max_length=20, null=True, blank=True)
    bank_username = models.CharField(max_length=50, null=True, blank=True)

    class Meta:
        verbose_name = _('guide')
        verbose_name_plural = _('guides')

    def save(self, *args, **kwargs):
        self.user_type = 2
        super().save(*args, **kwargs)

    def __str__(self):
        return self.username