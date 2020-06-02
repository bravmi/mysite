from django.contrib import admin
from django.shortcuts import redirect
from django.urls import include, path
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', lambda request: redirect('polls/', permanent=False)),
    path('polls/', include('polls.urls')),
    path('admin/', admin.site.urls),
    path('login/', auth_views.LoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
]
