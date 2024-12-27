from django.contrib import admin, messages
from django.db.models import Sum, F, Subquery, OuterRef, IntegerField, ExpressionWrapper
from zzap_car.tasks import fetch_parts_count_by_part_numbers_process

from zzap_core.models import Search, PartNumbersSearchResults, PartNumbersCount, Timeouts, SinglePartNumbers


@admin.register(Search)
class SearchAdmin(admin.ModelAdmin):
    list_display = ('search_string', 'search_time', )

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.exclude(search_string__isnull=True).exclude(search_string="")

@admin.register(SinglePartNumbers)
class SinglePartNumbersAdmin(admin.ModelAdmin):
    fields = ('part_number',)
    readonly_fields = ('brand_car', 'class_cat', 'created_at')
    list_display = ('part_number', 'brand_car', 'class_cat', 'created_at')
    search_fields = ('part_number', 'brand_car__brand_car', 'class_cat')
    actions = ('search_by_part_number', )

    def search_by_part_number(self, request, queryset=None):

        if queryset is None or len(queryset)>1:
            self.message_user(request, f"Ошибка: Выберите 1 артикул", messages.ERROR)
            return
        try:
            brand_data = list(queryset.values('part_number', 'brand_car'))
            brand_car = brand_data[0]['brand_car']
            part_number = brand_data[0]['part_number']
            fetch_parts_count_by_part_numbers_process.delay(brand_car, part_number, None)
            self.message_user(request, f"Успешно!", messages.SUCCESS)
        except Exception as e:
            self.message_user(request, f"Ошибка: {e}", messages.ERROR)

    search_by_part_number.short_description = "Искать по выбранному артикулу (light)"

    def save_model(self, request, obj, form, change):
        """Переопределяем сохранение модели в админке."""
        if not change:
            try:
                obj.fetch_data_from_api()
            except Exception as _ex:
                self.message_user(request,
                                  f"Ошибка: {_ex}",
                                  messages.SUCCESS)
        super().save_model(request, obj, form, change)


@admin.register(PartNumbersSearchResults)
class SearchResultsAdmin(admin.ModelAdmin):
    list_display = ('part_number', 'search_id', 'brand_car', 'class_cat',)


@admin.register(Timeouts)
class TimeoutsAdmin(admin.ModelAdmin):
    list_display = ('timeout_result', 'timeout_suggest', )


@admin.register(PartNumbersCount)
class PartNumbersCountAdmin(admin.ModelAdmin):
    list_display = ('part_number', 'class_cat', 'search_id', 'brand_car', 'count', 'created_at', 'difference')
    list_filter = ('brand_car', 'search_id__search_string', 'class_cat','part_number',)


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
