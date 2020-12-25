from django.contrib import admin
from .models import Stat, MatchBasic
from .forms import NameForm
# Register your models here.
admin.site.register(Stat)
admin.site.register(MatchBasic)
