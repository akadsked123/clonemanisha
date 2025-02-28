from django.contrib import admin
from .models import Institutes

class InstituteAdmin(admin.ModelAdmin):
    list_display = ('institute_name', 'acronym', 'institute_slug')
    list_display_links = ('institute_name', 'acronym', 'institute_slug')
    search_fields = ('institute_name', 'acronym')

admin.site.register(Institutes, InstituteAdmin)
