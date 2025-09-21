from django.contrib import admin
from import_export.admin import ImportExportModelAdmin
from .models import Product, Category

@admin.register(Product)
class ProductAdmin(ImportExportModelAdmin):
    pass

@admin.register(Category)
class CategoryAdmin(ImportExportModelAdmin):
    pass