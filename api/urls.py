from django.urls import path

from api import views

userpatterns = [
    path("users", views.UserList.as_view()),
    path("user/<int:pk>/", views.UserDetail.as_view()),
    path("register", views.UserRegister.as_view()),
    path("login", views.UserLogin.as_view()),
    path("logout", views.UserLogout.as_view()),
]

modelpatterns = [
    path("collection", views.CollectionView.as_view()),
    path("collection/<int:pk>", views.CollectionDetailView.as_view()),
]

urlpatterns = list(userpatterns + modelpatterns)
