from django.urls import path, include
from django.contrib import admin

from api import views

from rest_framework_simplejwt.views import (
    TokenRefreshView,
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include("api.urls"))
]

