from django.conf import settings
from django.db import models


class Book(models.Model):
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='livros'
    )
    id_bling = models.CharField(max_length=50, blank=True, null=True)
    code = models.CharField(max_length=50, blank=True)
    gtin_ean = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    description = models.TextField(blank=True)
    mark = models.CharField(max_length=255, blank=True, null=True)
    short_description = models.TextField(blank=True, null=True)
    url_external_images = models.TextField(blank=True)
    product_category = models.CharField(max_length=255, blank=True)
    year_published = models.DateField(blank=True, null=True)
    page_of_number = models.CharField(max_length=10, blank=True)
    author = models.CharField(max_length=255, blank=True)
    stock = models.CharField(max_length=20, blank=True)

    def __str__(self):
        return self.short_description or self.author or 'Livro'
