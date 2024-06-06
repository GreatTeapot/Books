import os
from io import BytesIO
from django.core.files import File
from django.db import models
from django.conf import settings
from django.template.loader import render_to_string
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from regauth.models import CustomUser


class Book(models.Model):
    name = models.CharField(max_length=35, unique=True, null=False)
    image = models.ImageField(upload_to='book_images/', null=True)
    author = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='books', null=True)
    total_pages = models.IntegerField(default=0)
    pdf = models.FileField(upload_to='book_pdfs/', blank=True, null=True)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        buffer = BytesIO()
        p = canvas.Canvas(buffer, pagesize=letter)
        p.drawString(100, 750, f"Book Title: {self.name}")
        p.drawString(100, 735, f"Author: {self.author.username}")
        p.drawString(100, 720, f"Total Pages: {self.total_pages}")

        # Assuming the image is saved locally and accessible
        if self.image:
            image_path = os.path.join(settings.MEDIA_ROOT, self.image.name)
            p.drawImage(image_path, 100, 600, width=200, height=200)

        p.showPage()
        p.save()

        # Save the PDF file to the FileField
        pdf_file_name = f'book_{self.id}.pdf'
        self.pdf.save(pdf_file_name, File(buffer), save=False)

        # Save the model again to store the PDF file
        super().save(*args, **kwargs)


class Page(models.Model):
    text = models.TextField()
    page_number = models.PositiveIntegerField(default=0)
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='pages')


class LastPage(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='recent_pages')
    page = models.ForeignKey(Page, on_delete=models.CASCADE, related_name='recent_pages')
