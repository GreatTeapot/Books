# views.py
from django.db.models import Avg, Count
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
    serializer_class = PageListSerializer

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
    serializer_class = PageSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request, book_id, page_id):

        try:
            page = Page.objects.get(pk=page_id, book=book_id)
            serializer = self.get_serializer(page, context={'request': request})

            return Response(serializer.data)
        except Page.DoesNotExist:
            return Response({"error": "Page not found"}, status=status.HTTP_404_NOT_FOUND)
        except Book.DoesNotExist:
            return Response({"error": "Book not found"}, status=status.HTTP_404_NOT_FOUND)


@extend_schema(tags=['Users'])
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
    """
    нужен  Access token
    Апи для добавление книгу в избранное.
    """
    serializer_class = FavoriteBookSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request, book_id):

        try:
            book = Book.objects.get(id=book_id)
            data = {'user': request.user.id, 'book': book.id}
            serializer = self.get_serializer(data=data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            return Response({"message": "Successfully added"}, status=status.HTTP_201_CREATED)
        except Book.DoesNotExist:
            return Response({"error": "Book not found"}, status=status.HTTP_404_NOT_FOUND)




@extend_schema(tags=['Books'])
class AddRatingView(generics.CreateAPIView):
    """
    нужен  Access token
    Апи для того чтобы ставить рейтинг книге от 1 до 10 также в этой же апишке есть вывод рейтинга
    на все книги который этот юзер ставил рейтинг
    """
    serializer_class = BookRatingSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request, book_id, ):
        book = Book.objects.get(id=book_id)
        data = {'user': request.user.id, 'book': book.id, 'rating': request.data.get('rating')}
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def get(self, request, book_id):
        try:
            book = Book.objects.get(id=book_id)
            average_rating = BookRating.objects.filter(book=book).exclude(rating__isnull=True).aggregate(Avg('rating'))[
                'rating__avg']
            if average_rating is not None:
                return Response({"average_rating": round(average_rating, 2)}, status=status.HTTP_200_OK)
            else:
                return Response({"average_rating": "No ratings yet"}, status=status.HTTP_200_OK)
        except Book.DoesNotExist:
            return Response({"error": "Book not found"}, status=status.HTTP_404_NOT_FOUND)


@extend_schema(tags=['Books'])
class AddFeedbackView(generics.CreateAPIView):
    """
    нужен  Access token
    Апи для того чтобы оставлять комментарий под книгой.
    Также есть его get который выводит все комментарии под этой книгой от всех юзеров
    """
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


@extend_schema(tags=['Users'])
class GetFavoriteBookView(generics.ListAPIView):
    """
        Нужен Access Token
        Апи для вывода всех сохраненных книг этого юзера
    """
    permission_classes = [IsAuthenticated]
    serializer_class = FavoriteBookSerializer

    def get(self, request, *args, **kwargs):
        favorite_books = FavoriteBook.objects.filter(user=request.user)
        serializer = self.get_serializer(favorite_books, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


@extend_schema(tags=['Books'])
class RemoveFromFavoritesView(generics.DestroyAPIView):
    """
    Нужен Access token
    Апи для удаления книги из избранного.
    """
    serializer_class = FavoriteBookSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return FavoriteBook.objects.filter(user=user)


@extend_schema(tags=['Books'])
class RemoveFeedbackView(generics.DestroyAPIView):
    """
    Нужен Access token
    Апи для удаления отзыва о книге.
    """
    serializer_class = BookFeedbackSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return BookFeedback.objects.filter(user=user)


@extend_schema(tags=['Books'])
class HistoryView(generics.ListAPIView):
    """
    Нужен Access token
    Апи для вывода истории просмотров книг пользователем.
    """
    serializer_class = BookListSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Book.objects.filter(pages__recent_pages__user=user)


@extend_schema(tags=['Books'])
class SearchByGenreView(generics.ListAPIView):
    """
    Нужен Access token
    Апи для поиска книг по жанрам.
    """
    serializer_class = BookListSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        genre_name = self.request.query_params.get('genre')
        if genre_name:
            return Book.objects.filter(genres__name=genre_name)
        else:
            return Book.objects.all()


@extend_schema(tags=['Books'])
class RecommendationView(generics.ListAPIView):
    """
    Нужен Access token
    Апи для вывода рекомендаций пользователю на основе его истории просмотров и жанров.
    """
    serializer_class = BookListSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        # Получаем жанры, которые пользователь предпочитает
        user_favorite_genres = user.favorite_genres.values_list('name', flat=True)
        # Сортируем книги по количеству совпадающих жанров
        return Book.objects.annotate(num_common_genres=Count('genres', filter=models.Q(genres__name__in=user_favorite_genres))) \
            .order_by('-num_common_genres')