# serializers.py
from rest_framework import serializers
from .models import Book, Page

class PageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Page
        fields = ['id', 'text', 'page_number', 'book']

class BookSerializer(serializers.ModelSerializer):
    pages = PageSerializer(many=True, read_only=True)

    class Meta:
        model = Book
        fields = ['id', 'name', 'image', 'author', 'total_pages', 'pdf', 'pages']

class BookListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = ['id', 'name', 'image', 'author', 'total_pages', 'pdf']
