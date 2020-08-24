import os
from celery import Celery
# set the default Django settings module for the 'celery' program. 
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'guide_match.settings')
app = Celery('guide_match')
app.config_from_object('guide_match.settings') 
app.autodiscover_tasks()