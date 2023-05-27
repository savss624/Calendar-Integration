"""
Core Urls
"""

from django.contrib import admin
from django.urls import path, include

from django_project.views import domain

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', domain, name="domain"),
    path("rest/v1/calendar/",
         include("calendar_api.urls"),
         name="calendar_api"),
]
