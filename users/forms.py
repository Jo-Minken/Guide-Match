from django import forms
from users.models import SiteUser as User
from users.models import Guide
 
class UserSignUpForm(forms.ModelForm):
    email = forms.EmailField(widget=forms.TextInput)
    username = forms.CharField(widget=forms.TextInput)
    password = forms.CharField(widget=forms.PasswordInput)
    repeat_password = forms.CharField(widget=forms.PasswordInput)
    phone = forms.CharField(widget=forms.TextInput)
 
    class Meta:
        model = User
        fields = [
            'username',
            'email',
            'phone',
            'password',
        ]

class GuideSignUpForm(forms.ModelForm):
    email = forms.EmailField(widget=forms.TextInput)
    password = forms.CharField(widget=forms.PasswordInput)
    repeat_password = forms.CharField(widget=forms.PasswordInput)
 
    class Meta:
        model = Guide
        fields = [
            'username',
            'email',
            'phone',
            'has_national_license',
            'region',
            'name_jp',
            'name_en',
        ]

class UserLogInForm(forms.ModelForm):
    username = forms.CharField(widget=forms.TextInput)
    password = forms.CharField(widget=forms.PasswordInput)
 
    class Meta:
        model = User
        fields = [
            'username',
            'password',
        ]