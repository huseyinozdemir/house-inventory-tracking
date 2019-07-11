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
    path('buildingDel/<slug:Tag>', views.buildingDel, name='buildingDel'),
    path('flat/<slug:Tag>', views.flat, name='flat'),
    path('flatDel/<slug:Tag>', views.flatDel, name='flatDel'),
    path('room/<slug:Tag>', views.room, name='room'),
    path('roomDel/<slug:Tag>', views.roomDel, name='roomDel'),
    path('fixture/<slug:Tag>', views.fixture, name='fixture'),
    path('fixtureDel/<slug:Tag>', views.fixtureDel, name='fixtureDel'),
]
