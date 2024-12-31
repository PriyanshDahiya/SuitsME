from django.contrib import admin
from .models import Product
from .models import Review
from .models import DailyQuote

class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'category')
    search_fields = ('name', 'category')

admin.site.register(Product, ProductAdmin)

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('content', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('content',)

@admin.register(DailyQuote)
class DailyQuoteAdmin(admin.ModelAdmin):
    list_display = ('quote', 'added_date')
    search_fields = ('quote',)