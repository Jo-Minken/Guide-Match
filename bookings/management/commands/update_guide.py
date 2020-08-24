from django.core.management.base import BaseCommand, CommandError
from bookings.models import Booking

class Command(BaseCommand):
    help = 'Update duplicate guide'

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        bookings = Booking.objects.all()
        for booking in bookings:
            booking.guide = booking.find_guide()
            booking.save()
            self.stdout.write(self.style.SUCCESS(f"{booking} updated"))

    