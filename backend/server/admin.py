from django.contrib import admin
from .models import Major, Course, Profile, Notebook, Team

admin.site.register(Major)
admin.site.register(Course)
admin.site.register(Profile)
admin.site.register(Notebook)
admin.site.register(Team)