import os

from django.conf import settings
from django.contrib import admin
from django.urls import path
from django.http import HttpResponse
from .models import *


class GenreInlineAdmin(admin.TabularInline):
    model = BookGenre
    extra = 3


class PageInlineAdmin(admin.TabularInline):
    model = Page
    fields = ["text", "page_number"]
    extra = 1


class BookAdmin(admin.ModelAdmin):
    list_display = ('name', 'author', 'total_pages', 'pdf')
    readonly_fields = ('total_pages', 'pdf')
    inlines = [PageInlineAdmin, GenreInlineAdmin]

    exclude = ('status',)

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('<path:object_id>/download/', self.download_pdf, name='book-download-pdf'),
        ]
        return custom_urls + urls

    def download_pdf(self, request, object_id, *args, **kwargs):
        book = self.get_object(request, object_id)
        if not book.pdf:
            return HttpResponse('PDF not available', status=404)

        pdf_path = os.path.join(settings.MEDIA_ROOT, book.pdf.name)
        with open(pdf_path, 'rb') as pdf_file:
            response = HttpResponse(pdf_file.read(), content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename={os.path.basename(pdf_path)}'
            return response





admin.site.register(Book, BookAdmin)
admin.site.register(Page)
admin.site.register(LastPage)
admin.site.register(Genre)