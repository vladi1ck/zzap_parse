from django.db import models

from zzap_car.models import BrandCar


class Search(models.Model):
    search_string = models.TextField()
    search_time = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Поиск'
        verbose_name_plural = 'Поиски'
        ordering = ['id']

    def __str__(self):
        return self.search_string

class PartNumbersSearchResults(models.Model):
    brand_id = models.ForeignKey(BrandCar, to_field='brand_id', on_delete=models.PROTECT)
    search_id = models.ForeignKey(Search, on_delete=models.CASCADE)
    part_number = models.CharField(max_length=255, null=False, blank=False)
    class_cat = models.CharField(max_length=255, null=False, blank=False)
    created_at = models.DateTimeField(auto_now_add=True)


    class Meta:
        verbose_name = 'Результат Поиска для Артикулов'
        verbose_name_plural = 'Результаты Поиска для Артикулов'
        constraints = [
            models.UniqueConstraint(fields=['brand_id', 'part_number'], name='unique_part_per_brand')
        ]
        ordering = ['id']

    def __str__(self):
        return f"{self.part_number} ({self.brand_id.brand_car})"

class PartNumbersCount(models.Model):
    brand_id = models.ForeignKey(BrandCar, to_field='brand_id', on_delete=models.PROTECT)
    search_id = models.ForeignKey(Search, on_delete=models.CASCADE)
    part_number = models.CharField(max_length=255, null=False, blank=False)
    count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Результат Поиска Запчасти (количество)'
        verbose_name_plural = 'Результаты Поиска Запчасти (количество)'
        ordering = ['-id']

    def __str__(self):
        return f"{self.part_number} ({self.brand_id.brand_car}) - {self.count}"