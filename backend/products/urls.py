from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ProductViewSet
from django.contrib.auth import views as auth_views
from . import views

router = DefaultRouter()
router.register(r'products', ProductViewSet)

urlpatterns = [
    path('api/', include(router.urls)),
    path('', views.home, name='home'),
    path('product/<int:pk>/', views.product_detail, name='product_detail'),
    path('like-product/', views.like_product, name='like_product'),
    path('get-next-product/', views.get_next_product, name='get_next_product'),  # New path for fetching next product
    path('profile/', views.profile, name='profile'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.custom_logout, name='logout'),
    path('signup/', views.signup, name='signup'),
    path('about/', views.about, name='about'),
    path('review/', views.review, name='review'),
    path('upload-csv/', views.upload_csv, name='upload_csv'),
    path('upload-exl/', views.upload_excel, name='upload_excel'),
    path('remove-from-wardrobe/<int:liked_product_id>/', views.remove_from_wardrobe, name='remove_from_wardrobe'),
    path('autocomplete-users/', views.autocomplete_users, name='autocomplete_users'),
    path('user/<str:username>/wardrobe/', views.view_user_wardrobe, name='view_user_wardrobe'),
    path('liked-products/', views.liked_products, name='liked_products'),
    path('add-to-wardrobe/<int:product_id>/', views.add_to_wardrobe, name='add_to_wardrobe'),

]
