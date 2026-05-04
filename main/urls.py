from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    path('register/', views.register_view, name='register_view'),
    path('profile/', views.profile_view, name='profile_view'),
    path('profile/edit/', views.edit_profile_view, name='edit_profile_view'),
    path('profile/password/', views.change_password_view, name='change_password_view'),
    path('profile/delete/', views.delete_account_view, name='delete_account_view'),
    path('profile/<str:username>/', views.profile_view, name='public_profile_view'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    