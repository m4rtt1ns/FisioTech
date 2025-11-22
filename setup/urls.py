from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views

# Imports para as fotos
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('core.urls')),
    
    # --- CORREÇÃO AQUI ---
    # Mudamos de 'registration/login.html' para apenas 'login.html'
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)