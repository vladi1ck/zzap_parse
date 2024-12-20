from django.contrib import admin

from zzap_core.models import Search, PartNumbersSearchResults, PartNumbersCount


@admin.register(Search)
class SearchAdmin(admin.ModelAdmin):
    list_display = ('search_string', 'search_time', )

@admin.register(PartNumbersSearchResults)
class SearchResultsAdmin(admin.ModelAdmin):
    list_display = ('part_number', 'search_id','brand_id', )

@admin.register(PartNumbersCount)
class PartNumbersCountAdmin(admin.ModelAdmin):
    list_display = ('part_number', 'search_id','brand_id', 'count')