import os
from io import BytesIO
from django.core.files import File
from django.db import models
from django.conf import settings
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from regauth.models import CustomUser



class Book(models.Model):
    name = models.CharField(max_length=35, unique=True, null=False)
    image = models.ImageField(upload_to='book_images/', null=True)
    author = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='books', null=True)
    total_pages = models.IntegerField(default=0, editable=False)
    pdf = models.FileField(upload_to='book_pdfs/', blank=True, null=True)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        self.total_pages = self.pages.count()
        super().save(update_fields=['total_pages'])

        buffer = BytesIO()
        p = canvas.Canvas(buffer, pagesize=letter)
        p.drawString(100, 750, f"Book Title: {self.name}")
        p.drawString(100, 735, f"Author: {self.author.username}")
        p.drawString(100, 720, f"Total Pages: {self.total_pages}")

        if self.image:
            image_path = os.path.join(settings.MEDIA_ROOT, self.image.name)
            p.drawImage(image_path, 100, 600, width=200, height=200)

        p.showPage()

        for page in self.pages.all():
            p.drawString(100, 700, f"Page Number: {page.page_number}")
            p.drawString(100, 685, page.text)
            p.showPage()

        p.save()

        pdf_file_name = f'book_{self.id}.pdf'
        self.pdf.save(pdf_file_name, File(buffer), save=False)

        super().save(update_fields=['pdf'])

class Page(models.Model):
    text = models.TextField()
    page_number = models.PositiveIntegerField()
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='pages')

    class Meta:
        unique_together = ('book', 'page_number')
        ordering = ['page_number']

    def save(self, *args, **kwargs):
        if not self.page_number:
            max_page = self.book.pages.aggregate(models.Max('page_number'))['page_number__max'] or 0
            self.page_number = max_page + 1
        super().save(*args, **kwargs)

from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

@receiver(post_save, sender=Page)
@receiver(post_delete, sender=Page)
def update_total_pages(sender, instance, **kwargs):
    book = instance.book
    book.total_pages = book.pages.count()
    book.save(update_fields=['total_pages'])


class LastPage(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='recent_pages')
    page = models.ForeignKey(Page, on_delete=models.CASCADE, related_name='recent_pages')
