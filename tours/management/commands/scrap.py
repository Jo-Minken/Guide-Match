from django.core.management.base import BaseCommand, CommandError
from tours.models import TourType, DayTour
import requests
from bs4 import BeautifulSoup
import re

class Command(BaseCommand):
    help = 'Scrap the data from otomo'

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        # write your scrap codes here

        pass