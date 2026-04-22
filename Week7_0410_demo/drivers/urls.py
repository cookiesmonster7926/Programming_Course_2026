from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('recruit/', views.recruit, name='recruit'),
    path('driver/<int:id>/', views.driver_detail, name='driver_detail'),
    path('driver/<int:id>/sign/', views.sign_driver, name='sign_driver'),
    path('driver/<int:id>/discard/', views.discard_driver, name='discard_driver'),
    path('driver/<int:id>/fire/', views.fire_driver, name='fire_driver'),
]
