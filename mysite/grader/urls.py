from django.urls import path
from django.conf.urls import url

from . import views

urlpatterns = [
    path('', views.login, name='index'),
    #path('login/', views.profile, name='login'),
    path('logout/', views.logout, name='logout'),
    path('profile/', views.profile, name='profile'),
    path('userhome/', views.userhome, name='userhome'),
    path('topics', views.topics, name='topics'),
    path('essay/', views.essay, name='essay'),
    path('scoring/', views.scoring, name='scoring'),
    path('admin/accessdb/', views.accessdb, name='accessdb'),
    #path('testing/', views.testing, name='testing'),
    #path('dev/', views.dev, name='dev')

]