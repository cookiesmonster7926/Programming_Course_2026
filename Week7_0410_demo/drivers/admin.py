from django.contrib import admin
from .models import Driver


@admin.register(Driver)
class DriverAdmin(admin.ModelAdmin):
    list_display = ('name', 'team', 'points', 'is_signed')
    search_fields = ('name', 'team')
    list_filter = ('team', 'is_signed')
    list_editable = ('is_signed',)
    ordering = ('-points',)
