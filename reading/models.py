import os

from django.core.validators import MinValueValidator, MaxValueValidator
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from regauth.models import CustomUser
from django.db import models
from django.conf import settings
from django.core.files import File
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from regauth.models import CustomUser


class Genre(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name


class Book(models.Model):
    STATUS_CHOICES = [
        ('', ''),
        ('reading', 'reading'),
        ('read', 'read'),
    ]

    name = models.CharField(max_length=35, unique=True, null=False)
    image = models.ImageField(null=True, blank=True, upload_to='book_images/')
    author = models.CharField(max_length=60, null=False, blank=False)
    total_pages = models.IntegerField(default=0, editable=False)
    pdf = models.FileField(upload_to='book_pdfs/', blank=True, null=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='')

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.total_pages = self.pages.count()
        super().save(update_fields=['total_pages'])

        buffer = BytesIO()
        p = canvas.Canvas(buffer, pagesize=letter)
        p.drawString(100, 750, f"Book Title: {self.name}")
        p.drawString(100, 735, f"Author: {self.author}")
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


class BookStatus(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    status = models.CharField(max_length=10, choices=Book.STATUS_CHOICES, default='')

    class Meta:
        unique_together = ('user', 'book')


class BookGenre(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    genre = models.ForeignKey(Genre, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('book', 'genre')


class Page(models.Model):
    text = models.TextField()
    page_number = models.DecimalField(max_digits=6, decimal_places=1, validators=[MinValueValidator(0), MaxValueValidator(9999.9)])
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='pages')

    class Meta:
        unique_together = ('book', 'page_number')
        ordering = ['page_number']

    def save(self, *args, **kwargs):
        if not self.page_number:
            max_page = self.book.pages.aggregate(models.Max('page_number'))['page_number__max'] or 0
            self.page_number = max_page + 1
        super().save(*args, **kwargs)


@receiver(post_save, sender=Page)
@receiver(post_delete, sender=Page)
def update_total_pages(sender, instance, **kwargs):
    book = instance.book
    book.total_pages = book.pages.count()
    book.save(update_fields=['total_pages'])


class LastPage(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='recent_pages')
    page = models.ForeignKey(Page, on_delete=models.CASCADE, related_name='recent_pages')


class FavoriteBook(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='favorite_books')
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='favorited_by')

    # class Meta:
    #     unique_together = ('user', 'book')


class BookRating(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='book_ratings')
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='ratings')
    rating = models.PositiveIntegerField(null=True, blank=True)

    class Meta:
        # unique_together = ('user', 'book')
        constraints = [
            models.CheckConstraint(check=models.Q(rating__gte=1) & models.Q(rating__lte=10), name='rating_range')
        ]


class BookFeedback(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='book_feedbacks')
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='feedbacks')
    feedback = models.TextField()

    # class Meta:
    #     unique_together = ('user', 'book')
