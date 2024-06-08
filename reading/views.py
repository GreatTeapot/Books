# views.py
from drf_spectacular.utils import extend_schema
from rest_framework import generics
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .models import Book, Page
from .serializers import *


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
    queryset = Page.objects.all()
    serializer_class = PageSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        page_id = self.kwargs.get('page_id')
        try:
            page = Page.objects.get(pk=page_id)
            serializer = self.get_serializer(page)

            LastPage.objects.update_or_create(
                user=request.user,
                defaults={'page': page}
            )

            return Response(serializer.data)
        except Page.DoesNotExist:
            return Response({"error": "Page not found"}, status=status.HTTP_404_NOT_FOUND)


@extend_schema(tags=['Books'])
class LastPageView(generics.RetrieveAPIView):
    """
        Здесь нужен access токен и эндроинт выдает последнюю страницу книги  которую он прочитал
    """
    serializer_class = LastPageSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        try:
            last_page = LastPage.objects.get(user=request.user)
            serializer = self.get_serializer(last_page)
            return Response(serializer.data)
        except LastPage.DoesNotExist:
            return Response({"error": "No last page found for user"}, status=status.HTTP_404_NOT_FOUND)


@extend_schema(tags=['Books'])
class AddToFavoritesView(generics.CreateAPIView):
    # queryset = FavoriteBook.objects.all()
    serializer_class = FavoriteBookSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request, book_id):
        try:
            # book_id = kwargs.get('book_id')
            book = Book.objects.get(id=book_id)
            data = {'user': request.user.id, 'book': book.id}
            serializer = self.get_serializer(data=data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Book.DoesNotExist:
            return Response({"error": "Book not found"}, status=status.HTTP_404_NOT_FOUND)




@extend_schema(tags=['Books'])
class AddRatingView(generics.CreateAPIView):
    serializer_class = BookRatingSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request, book_id, ):
        book = Book.objects.get(id=book_id)
        data = {'user': request.user.id, 'book': book.id, 'rating': request.data.get('rating')}
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


@extend_schema(tags=['Books'])
class AddFeedbackView(generics.CreateAPIView):
    serializer_class = BookFeedbackSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request, book_id):
        try:
            book = Book.objects.get(id=book_id)
            data = {'user': request.user.id, 'book': book.id, 'feedback': request.data.get('feedback')}
            serializer = self.get_serializer(data=data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        except Book.DoesNotExist:
            return Response({"error": "Book not found"}, status=status.HTTP_404_NOT_FOUND)

    def get(self, request, book_id):
        try:
            book = Book.objects.get(id=book_id)
            feedbacks = BookFeedback.objects.filter(book=book)
            serializer = self.get_serializer(feedbacks, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Book.DoesNotExist:
            return Response({"error": "Book not found"}, status=status.HTTP_404_NOT_FOUND)