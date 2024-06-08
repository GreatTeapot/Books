# urls.py
from django.urls import path
from .views import *

urlpatterns = [
    path('books/', BookListView.as_view(), name='book-list'),
    path('books/<int:book_id>/', BookDetailView.as_view(), name='book-detail'),
    path('books/<int:book_id>/pages/', PageListView.as_view(), name='page-list'),
    # path('books/<int:book_id>/pages/<int:page_id>/', PageDetailView.as_view(), name='page-detail'),
    path('pages/<int:page_id>/', PageDetailView.as_view(), name='page-detail'),
    path('users/last-page/', LastPageView.as_view(), name='last-page'),
    path('books/<int:book_id>/fav/', AddToFavoritesView.as_view(), name='add-to-favorites'),
    path('books/<int:book_id>/rating/', AddRatingView.as_view(), name='add-rating'),
    path('books/<int:book_id>/feedback/', AddFeedbackView.as_view(), name='add-feedback'),
]