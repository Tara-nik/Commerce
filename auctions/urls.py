from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("watchlist", views.watchlist, name="watchlist"),
    path('add_to_watchlist/<int:listing_id>/', views.add_to_watchlist, name='add_to_watchlist'),
    path('delete_watchlist/<int:listing_id>/', views.delete_watchlist, name='delete_watchlist'),
    path('create_listing/', views.create_listing, name='create_listing'),
    path("active_list/", views.active_list, name='active_list'),
    path("detail_list/<str:title>/", views.detail_list, name='detail_list'),
    path("categories/", views.categories, name="categories"),
    path("category/<str:category>/", views.category_listings, name="category_listings"),
    path("comment/<str:title>/", views.comment, name="comment"),
    path('bid/<int:listing_id>/', views.bid, name="bid"),
    path("close/<int:listing_id>/", views.close, name="close"),
    path("closed_listing/", views.closed_listing, name="closed_listing"),
]