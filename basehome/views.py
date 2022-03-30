from django.shortcuts import render
from django.views.generic import TemplateView

# Create your views here.
class HomeView(TemplateView):
    template_name = "basic/home.html"

class AboutView(TemplateView):
    template_name = "basic/about.html"