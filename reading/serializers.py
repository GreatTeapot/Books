# serializers.py
from rest_framework import serializers
from .models import *


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = ['name']


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
    genre = serializers.SerializerMethodField()

    class Meta:
        model = Book
        fields = ['id', 'name', 'image', 'author', 'total_pages', 'pdf', 'genre']

    def get_genre(self, obj):
        book_genres = BookGenre.objects.filter(book=obj)
        return [i.genre.name for i in book_genres]


class LastPageSerializer(serializers.ModelSerializer):
    page = PageSerializer(read_only=True)

    class Meta:
        model = LastPage
        fields = ['user', 'page']


class FavoriteBookSerializer(serializers.ModelSerializer):
    class Meta:
        model = FavoriteBook
        fields = ['user', 'book']


    def create(self, validated_data):
        return BookFeedback.objects.create(**validated_data)


class BookRatingSerializer(serializers.ModelSerializer):
    class Meta:
        model = BookRating
        fields = ['user', 'book', 'rating']

    def validate_rating(self, value):
        if value < 1 or value > 10:
            raise serializers.ValidationError("Rating must be between 1 and 10.")
        return value


    def create(self, validated_data):
        return BookFeedback.objects.create(**validated_data)


class BookFeedbackSerializer(serializers.ModelSerializer):
    class Meta:
        model = BookFeedback
        fields = ['user', 'book', 'feedback']

    def create(self, validated_data):
        return BookFeedback.objects.create(**validated_data)