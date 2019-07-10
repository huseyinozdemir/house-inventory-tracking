from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('dashboard', views.dashboard, name='dashboard'),
    path('buildings', views.buildings, name='buildings'),
    path('flats', views.flats, name='flats'),
    path('rooms', views.rooms, name='rooms'),
    path('fixtures', views.fixtures, name='fixtures'),
    path('logout', views.logout, name='logout'),
    path('building/<slug:Tag>', views.building, name='building'),
]
