from django.shortcuts import render

# Create your views here.
import os
import subprocess
import uuid

from django.contrib import messages
from django.contrib.auth import logout, login
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render, redirect

from django.views import View
from django.views.decorators.csrf import csrf_exempt

from home.forms import UserForm


class Home(View):
    def get(self, request):
        return render(request,
                      template_name='home.html')

class Registration(View):
    def get(self, request):
        form = UserForm()
        return render(request=request,
                      template_name="registration/signup.html",
                      context={"register_form": form})

    def post(self, request):
        form = UserForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Successfully registered")
            return redirect("login")
        messages.error(request, "Registration failed. Please try again!")
        return render(request=request,
                      template_name="registration/signup.html",
                      context={"form": form})


class SignOutView(View):
    def get(self, request):
        logout(request)
        return HttpResponseRedirect('/login')
