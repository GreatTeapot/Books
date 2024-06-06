# urls.py
from django.urls import path
from .views import BookListView, BookDetailView, PageListView, PageDetailView

urlpatterns = [
    path('books/', BookListView.as_view(), name='book-list'),
    path('books/<int:book_id>/', BookDetailView.as_view(), name='book-detail'),
    path('books/<int:book_id>/pages/', PageListView.as_view(), name='page-list'),
    path('pages/<int:page_id>/', PageDetailView.as_view(), name='page-detail'),
]
