from django.db import models
from django.db.models import Count, Avg
import random, math
from django.utils.text import slugify
from users.models import Guide

# Create your models here.
class TourType(models.Model):
    name = models.CharField(max_length=50)

    def gen_thumbnail_path(self):
        num = random.randint(1, 6)
        return f"/static/img/destination/{num}.png"

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name

class DayTour(models.Model):
    name = models.CharField(max_length=200)
    region = models.CharField(max_length=100)
    tour_price_without_tax = models.IntegerField()
    duration = models.FloatField()
    description_header = models.CharField(max_length=500)
    description = models.TextField()
    content = models.TextField()
    tourtypes = models.ManyToManyField(TourType)
    slug = models.SlugField(max_length=200, blank=True, null=True)

    by_guide = models.ForeignKey(Guide, blank=True, null=True, on_delete=models.CASCADE)
    approved = models.BooleanField(default=True)

    def gen_thumbnail_path(self):
        num = random.randint(1, 6)
        return f"/static/img/place/{num}.png"

    def gen_slug_from_name(self):
        tour_name = self.name
        return slugify(tour_name, allow_unicode=True)

    def get_tax_in_price(self):
        tax_rate = 0.1
        tax_in_price = self.tour_price_without_tax * (1 + tax_rate)
        return '{0:.2f}'.format(tax_in_price)

    def get_tourprice_for_guide(self):
        hour_pay = 28
        tour_price = self.duration * hour_pay / 0.6
        return tour_price

    def get_review_count(self):
        return DayTour.objects.filter(pk=self.pk)\
                              .annotate(review_count=Count('booking__review'))\
                              .first().review_count

    def get_review_score(self):
        score = DayTour.objects.filter(pk=self.pk)\
                               .annotate(review_score=Avg("booking__review__score"))\
                               .first().review_score or 0
        score = math.ceil(score) 
        return ["fa-star"] * score + ["fa-star-o"] * (5 - score)
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = self.gen_slug_from_name()
        
        super().save(*args, **kwargs)

    class Meta:
        ordering = ['name']
        indexes = [
            models.Index(fields=['region']),
        ]

    def __str__(self):
        return f"({self.region}) - {self.name}"
