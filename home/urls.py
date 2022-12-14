from django.urls import path
from django.contrib.auth import views as auth_views

from home import views
from django.conf.urls.static import static

from second_sale import settings

urlpatterns = [
    path('home/', views.Home.as_view(), name='homepage'),
    path('login/', auth_views.LoginView.as_view(), name='login'),
    path("register/", views.Registration.as_view(), name='signup'),
    path('logout/', views.SignOutView.as_view(), name='logout'),
    ]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
