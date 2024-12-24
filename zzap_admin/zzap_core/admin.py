from django.contrib import admin, messages
from django.db.models import Sum, F, Subquery, OuterRef, IntegerField, ExpressionWrapper
from datetime import datetime, timedelta

from zzap_core.models import Search, PartNumbersSearchResults, PartNumbersCount, Timeouts


@admin.register(Search)
class SearchAdmin(admin.ModelAdmin):
    list_display = ('search_string', 'search_time', )


@admin.register(PartNumbersSearchResults)
class SearchResultsAdmin(admin.ModelAdmin):
    list_display = ('part_number', 'search_id', 'brand_car', )


@admin.register(Timeouts)
class TimeoutsAdmin(admin.ModelAdmin):
    list_display = ('timeout_result', 'timeout_suggest', )


@admin.register(PartNumbersCount)
class PartNumbersCountAdmin(admin.ModelAdmin):
    list_display = ('part_number', 'search_id', 'brand_car', 'count', 'created_at', 'difference')
    list_filter = ('part_number', 'search_id__search_string', 'brand_car')


    def get_queryset(self, request):
        qs = super().get_queryset(request)
        latest_sales = qs.filter(
            created_at=Subquery(
                qs.filter(part_number=OuterRef('part_number'))
                .order_by('-created_at')
                .values('created_at')[:1]
            )
        ).order_by('-created_at')
        return latest_sales

    def difference(self, obj):
        previous_record = (
            PartNumbersCount.objects.filter(part_number=obj.part_number, created_at__lt=obj.created_at)
            .order_by('-created_at')
            .first()
        )
        if previous_record:
            return obj.count - previous_record.count
        return None

    difference.short_description = 'Разница с предыдущей датой'

    def change_view(self, request, object_id, form_url='', extra_context=None):
        obj = self.get_object(request, object_id)

        all_records = PartNumbersCount.objects.filter(part_number=obj.part_number).order_by('created_at')

        total_negative_difference = 0
        previous_record = None

        for record in all_records:
            if previous_record:
                record.difference = record.count - previous_record.count
            else:
                record.difference = 0
            previous_record = record

            if record.difference < 0:
                total_negative_difference += abs(record.difference)

        extra_context = extra_context or {}
        extra_context['related_records'] = all_records
        extra_context['total_negative_difference'] = total_negative_difference

        return super().change_view(request, object_id, form_url, extra_context=extra_context)


class PartNumberSummaryAdmin(admin.ModelAdmin):
    change_list_template = "admin/partnumber_summary_change_list.html"
    list_filter = ('part_number', 'search_id')

    def changelist_view(self, request, extra_context=None):
        part_number = request.resolver_match.kwargs.get('object_id')

        latest_records = PartNumbersCount.objects.filter(
            part_number=part_number,
        ).filter(
            created_at=Subquery(
                PartNumbersCount.objects.filter(part_number=OuterRef('part_number'))
                .order_by('-created_at')
                .values('created_at')[:1]
            )
        ).order_by('created_at')

        total_negative_difference = 0
        previous_record = None

        for record in latest_records:
            if previous_record:
                difference = record.count - previous_record.count
                record.difference = difference
                if difference < 0:
                    total_negative_difference += abs(difference)
            previous_record = record

        extra_context = {
            'related_records': latest_records,
            'total_negative_difference': total_negative_difference
        }

        return super().changelist_view(request, extra_context=extra_context)

# admin.site.register(PartNumberSummaryAdmin)
