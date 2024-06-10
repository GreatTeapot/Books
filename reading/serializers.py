# serializers.py
from django.db.models import Avg
from drf_spectacular.utils import extend_schema_field
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

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        user = self.context['request'].user
        book = instance.book

        book_status, created = BookStatus.objects.get_or_create(user=user, book=book)
        if book_status.status != 'read':
            book_status.status = 'reading'
            book_status.save()

        LastPage.objects.update_or_create(
            user=user,
            defaults={'page': instance}
        )

        return representation


class PageListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Page
        fields = ['id',  'page_number', 'book']


class BookListSerializer(serializers.ModelSerializer):
    genre = serializers.SerializerMethodField()
    average_rating = serializers.SerializerMethodField()
    status = serializers.SerializerMethodField()

    class Meta:
        model = Book
        fields = ['id', 'name', 'image', 'author', 'total_pages', 'pdf', 'genre', 'average_rating', 'status']

    @extend_schema_field(serializers.ListField(child=serializers.CharField()))
    def get_genre(self, obj):
        book_genres = BookGenre.objects.filter(book=obj)
        return [i.genre.name for i in book_genres]

    @extend_schema_field(serializers.FloatField(allow_null=True))
    def get_average_rating(self, obj):
        average_rating = BookRating.objects.filter(book=obj).exclude(rating__isnull=True).aggregate(Avg('rating'))[
            'rating__avg']
        if average_rating is not None:
            return round(average_rating, 2)
        return None

    @extend_schema_field(serializers.CharField())
    def get_status(self, obj):
        user = self.context['request'].user
        book_status = BookStatus.objects.filter(user=user, book=obj).first()
        if book_status:
            return book_status.status
        return ''


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
        user = validated_data['user']
        book = validated_data['book']

        if FavoriteBook.objects.filter(user=user, book=book).exists():
            raise serializers.ValidationError("This book is already in favorites.")

        return FavoriteBook.objects.create(**validated_data)


class BookRatingSerializer(serializers.ModelSerializer):
    class Meta:
        model = BookRating
        fields = ['user', 'book', 'rating']

    def validate_rating(self, value):
        if value < 1 or value > 10:
            raise serializers.ValidationError("Rating must be between 1 and 10.")
        return value

    def create(self, validated_data):
        return BookRating.objects.create(**validated_data)


class BookFeedbackSerializer(serializers.ModelSerializer):
    class Meta:
        model = BookFeedback
        fields = ['user', 'book', 'feedback']

    def create(self, validated_data):
        return BookFeedback.objects.create(**validated_data)