from django.contrib import admin

from zzap_core.models import Search


@admin.register(Search)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('search_string', 'search_time', )