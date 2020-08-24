from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from django.views.generic import CreateView
from django.views import View
from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.auth import login, logout, authenticate

from users.forms import UserSignUpForm, UserLogInForm, GuideSignUpForm

class UserSignUp(SuccessMessageMixin, CreateView):
    form_class = UserSignUpForm
    template_name = 'user-register.html'
    success_message = 'Your account has been created'
    success_url = reverse_lazy('index')
 
    def form_valid(self, form):
        context = {'form': form, }
        password = form.cleaned_data['password']
        repeat_password = form.cleaned_data['repeat_password']
        if password != repeat_password:
            messages.error(self.request, "Passwords do not Match", extra_tags='alert alert-danger')
            return render(self.request, self.template_name, context)
        
        user = form.save(commit=False)
        user.set_password(password)
        user.is_staff = False
        user.save()
        
        login(self.request, user)
        messages.info(self.request, f"{ user.username }, {self.success_message}")
        return HttpResponseRedirect(self.success_url)

class GuideSignUp(SuccessMessageMixin, CreateView):
    form_class = GuideSignUpForm
    template_name = 'guide-register.html'
    success_message = 'Your account has been created'
    success_url = reverse_lazy('index')
 
    def form_valid(self, form):
        context = {'form': form, }
        password = form.cleaned_data['password']
        repeat_password = form.cleaned_data['repeat_password']
        if password != repeat_password:
            messages.error(self.request, "Passwords do not Match", extra_tags='alert alert-danger')
            return render(self.request, self.template_name, context)
        
        user = form.save(commit=False)
        user.set_password(password)
        user.is_staff = False
        user.save()
        
        login(self.request, user)
        messages.info(self.request, f"{ user.username }, {self.success_message}")
        return HttpResponseRedirect(self.success_url)

class UserLogOut(View):
    success_url = reverse_lazy('index')
    def get(self, request, *args, **kwargs):
        logout(self.request)
        return HttpResponseRedirect(self.success_url)

class UserLogIn(SuccessMessageMixin, View):
    form_class = UserLogInForm
    template_name = 'user-login.html'
    success_message = 'Welcome back!'
    success_url = reverse_lazy('index')

    def get(self, request, *args, **kwargs):
        form = self.form_class
        return render(self.request, self.template_name, {"form": form})

    def post(self, request, *args, **kwargs):
        form = request.POST

        username = form.get('username')
        password = form.get('password')

        user = authenticate(username=username, password=password)
        
        if user is None:
            messages.error(self.request, "Login Failed: Wrong Password", extra_tags='alert alert-danger')
            return render(self.request, self.template_name, {"form": self.form_class})
        
        login(self.request, user)
        messages.info(self.request, f"{ user.username }, {self.success_message}")
        self.object = user 

        self.success_url = self.request.GET.get("next", self.success_url)
        return HttpResponseRedirect(self.success_url)


from django.http import JsonResponse
from bookings.models import Booking, Message
import json
def message_create(request, *args, **kwargs):
    booking = get_object_or_404(Booking, pk=kwargs.get('booking_id'))

    if (request.user.user_type == 1 and booking.customer.pk == request.user.pk) \
        or (request.user.user_type == 2 and booking.guide.pk == request.user.pk):

        message = Message()
        message.booking = booking

        body_unicode = request.body.decode('utf-8')
        body = json.loads(body_unicode)

        message.note = body.get("message")
        message.save()

        return JsonResponse({'status': 200})

    return JsonResponse({'status': 403})

        