"""Module for admin pages"""
from django.contrib import admin


from .models import Appointment, Question, Answer

admin.site.register(Appointment)
admin.site.register(Question)
admin.site.register(Answer)
