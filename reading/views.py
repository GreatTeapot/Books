# views.py
from drf_spectacular.utils import extend_schema
from rest_framework import generics
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .models import Book, Page
from .serializers import BookSerializer, BookListSerializer, PageSerializer


@extend_schema(tags=['Books'])
class BookListView(generics.ListAPIView):
    """
    Здесь не нужен access токен так как этот эндпоинт будет публичным
    он выдает информацию о книгах но не их страницы
    """

    permission_classes = [AllowAny]
    queryset = Book.objects.all()
    serializer_class = BookListSerializer


@extend_schema(tags=['Books'])
class BookDetailView(generics.RetrieveAPIView):
    """
       Здесь не нужен access токен так как этот эндпоинт будет публичным
       он выдает информацию о книге но не его страницы
    """
    permission_classes = [AllowAny]
    queryset = Book.objects.all()
    serializer_class = BookListSerializer

    def get(self, request, *args, **kwargs):
        book_id = self.kwargs.get('book_id')
        try:
            book = Book.objects.get(pk=book_id)
            serializer = self.get_serializer(book)
            return Response(serializer.data)
        except Book.DoesNotExist:
            return Response({"error": "Book not found"}, status=status.HTTP_404_NOT_FOUND)


@extend_schema(tags=['Books'])
class PageListView(generics.ListAPIView):
    """
       Здесь нужен access токен и эндроинт выдает все страницы для этой книгы
    """
    permission_classes = [IsAuthenticated]
    serializer_class = PageSerializer

    def get(self, request, *args, **kwargs):
        book_id = self.kwargs.get('book_id')
        try:
            book = Book.objects.get(pk=book_id)
            pages = Page.objects.filter(book=book)
            serializer = self.get_serializer(pages, many=True)
            return Response(serializer.data)
        except Book.DoesNotExist:
            return Response({"error": "Book not found"}, status=status.HTTP_404_NOT_FOUND)


@extend_schema(tags=['Books'])
class PageDetailView(generics.RetrieveAPIView):
    """
       Здесь нужен access токен и эндроинт выдает определенную страницу,
       эндроинт нужен для чтения книги юзером
    """
    permission_classes = [IsAuthenticated]
    serializer_class = PageSerializer

    def get(self, request, *args, **kwargs):
        page_id = self.kwargs.get('page_id')

        try:
            page = Page.objects.get(pk=page_id)
            serializer = self.get_serializer(page)
            return Response(serializer.data)
        except Page.DoesNotExist:
            return Response({"error": "Page not found"}, status=status.HTTP_404_NOT_FOUND)
