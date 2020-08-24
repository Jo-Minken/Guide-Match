from django import forms
from bookings.models import Booking, Payment
from bookings.validators import validate_tourdate
 
class PaymentForm(forms.ModelForm):
    payment_method = forms.ChoiceField(widget=forms.RadioSelect(), choices=Payment.PAYMENT_CHOICES, required = True)
    tourdate = forms.CharField(widget=forms.HiddenInput, validators=[validate_tourdate])
    class Meta:
        model = Booking
        fields = [
            'payment_method',
        ]