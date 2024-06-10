# urls.py
from django.urls import path
from .views import *

urlpatterns = [
    path('books/', BookListView.as_view(), name='book-list'),
    path('books/<int:book_id>/', BookDetailView.as_view(), name='book-detail'),
    path('books/<int:book_id>/pages/', PageListView.as_view(), name='page-list'),
    path('books/<int:book_id>/pages/<int:page_id>/', PageDetailView.as_view(), name='page-detail'),
    path('users/last-page/', LastPageView.as_view(), name='last-page'),
    path('books/<int:book_id>/fav/', AddToFavoritesView.as_view(), name='add-to-favorites'),
    path('users/fav/', GetFavoriteBookView.as_view(), name='add-to-favorites'),
    path('books/<int:book_id>/rating/', AddRatingView.as_view(), name='add-rating'),
    path('books/<int:book_id>/feedback/', AddFeedbackView.as_view(), name='add-feedback'),
    path('books/<int:book_id>/rm-favs/', RemoveFromFavoritesView.as_view(), name='rm-favorites'),
    path('books/<int:book_id>/feedback/<int:pk>/rm/', RemoveFeedbackView.as_view(), name='remove-feedback'),
    path('books/history/', HistoryView.as_view(), name='history'),
    path('books/sch-genre/', SearchByGenreView.as_view(), name='search-by-genre'),
    path('books/rec/', RecommendationView.as_view(), name='recommendation'),

]
