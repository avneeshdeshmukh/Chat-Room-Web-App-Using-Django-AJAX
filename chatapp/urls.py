from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.login_user, name='login_user'),
    path('signup/', views.signup_user, name='signup_user'),
    path('logout/', views.logout_user, name='logout_user'),
    path('createRoom/', views.createRoom, name='createRoom'),
    path('joinRoom/', views.joinRoom, name='joinRoom'),
    path('room/<int:roomID>/', views.room, name='room'),
    path('send/', views.send, name='send'),
    path('getMessages/<int:roomID>/', views.getMessages, name='getMessages'),
    path('userProfile/', views.userProfile, name='userProfile'),
    path('roomDetails/<int:roomID>/', views.roomDetails, name='roomDetails'),
    path('editProfile/', views.editProfile, name='editProfile'),
    path('changePassword/', views.changePassword, name='changePassword'),
    path('deleteAccount/', views.deleteAccount, name='deleteAccount'),
    path('deleteRoom/<int:roomID>', views.deleteRoom, name='deleteRoom'),
    path('leaveRoom/<int:roomID>', views.leaveRoom, name='leaveRoom'),
    path('removeMember/<int:roomID>/<str:member>', views.removeMember, name='removeMember'),
    path('checkMembership/<int:roomID>/', views.check_membership, name='check_membership'),


]
