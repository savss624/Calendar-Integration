"""
Views for core.
"""

from django.shortcuts import redirect


def domain(request):
    return redirect("google_calendar_init")