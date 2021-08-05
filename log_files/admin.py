from django.contrib import admin
from .models import Gost, Professions, Labor_functions, Tests, Users, Answers

admin.site.register(Gost)
admin.site.register(Professions)
admin.site.register(Labor_functions)
admin.site.register(Tests)
admin.site.register(Users)
admin.site.register(Answers)