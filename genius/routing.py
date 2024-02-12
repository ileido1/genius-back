# routing.py

from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from django.urls import path

from genius.api import views
from .consumers import YourConsumer

application = ProtocolTypeRouter({
    'websocket': AuthMiddlewareStack(
        URLRouter(
            [
                path('ws/cvs_process/', views.ProcessDataView.as_view()),
                # Agrega más rutas si es necesario
            ]
        )
    ),
})
