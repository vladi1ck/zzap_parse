from django.db import models


class BrandCar(models.Model):
    brand_car = models.CharField(max_length=255, null=False, blank=False)
    brand_id = models.CharField(max_length=255, null=False, blank=False)

    class Meta:
        verbose_name = 'Бренд'
        verbose_name_plural = 'Бренды'
        ordering = ['id']

    def __str__(self):
        return self.brand_car


class ModelCar(models.Model):
    brand = models.ForeignKey(BrandCar, on_delete=models.PROTECT)
    model_car = models.CharField(max_length=255, null=False, blank=False)
    model_id = models.CharField(max_length=255, null=False, blank=False)

    class Meta:
        verbose_name = 'Модель'
        verbose_name_plural = 'Модели'
        ordering = ['id']

    def __str__(self):
        return f'{self.brand} {self.model_car}'


class Car(models.Model):
    brand_car = models.ForeignKey(BrandCar, on_delete=models.PROTECT)
    model_car = models.ForeignKey(ModelCar, on_delete=models.PROTECT)

    class Meta:
        verbose_name = 'Машина'
        verbose_name_plural = 'Машины'
        ordering = ['id']

    def __str__(self):
        return f'{self.brand_car} {self.model_car}'