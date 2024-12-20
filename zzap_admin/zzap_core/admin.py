from django.contrib import admin

from zzap_core.models import Search, SearchResults


@admin.register(Search)
class SearchAdmin(admin.ModelAdmin):
    list_display = ('search_string', 'search_time', )

@admin.register(SearchResults)
class SearchResultsAdmin(admin.ModelAdmin):
    list_display = ('part_number', 'search_id','brand_id', )
