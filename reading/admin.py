from django.contrib import admin
# Register your models here.
from .models import *
from django.contrib import admin


class PageInlineAdmin(admin.TabularInline):
    model = Page
    fields = [
        "text",
        "page_number"
    ]


class BookAdmin(admin.ModelAdmin):
    list_display = ('name', 'author', 'total_pages', 'pdf')
    readonly_fields = ('pdf',)
    inlines = [PageInlineAdmin]


admin.site.register(Book, BookAdmin)
admin.site.register(Page)