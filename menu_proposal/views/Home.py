from django.urls import reverse_lazy
from django.views.generic import *
from django import forms
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.shortcuts import render


def home(request):
    return render(request, "index.html")
