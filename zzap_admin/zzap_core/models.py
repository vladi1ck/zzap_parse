from django.db import models


class Search(models.Model):
    search_string = models.TextField()
    search_time = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Поиск'
        verbose_name_plural = 'Поиски'
        ordering = ['id']

    def __str__(self):
        return {self.search_string}
