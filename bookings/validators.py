from django.core.exceptions import ValidationError
from datetime import date, timedelta, datetime
from dateutil.relativedelta import relativedelta

def validate_tourdate(value):

    tourdate_min = date.today() + timedelta(days=3)
    tourdate_max = date.today() + relativedelta(months=3)
    value = datetime.strptime(str(value), '%Y-%m-%d').date()

    if(value < tourdate_min or value > tourdate_max):
        raise ValidationError("The tour date should be 3 days later and within 3 months")