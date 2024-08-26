from django.urls import path

from api import views

userpatterns = [
    path("register", views.UserRegister.as_view()),
    path("login", views.UserLogin.as_view()),
    path("logout", views.UserLogout.as_view()),
]

modelpatterns = [
    path("collection", views.CollectionView.as_view()),
    path("collections", views.CollectionList.as_view()),
    path("collection_selector", views.CollectionSelector.as_view()),
    path(
        "course_schedules/<int:course_id>",
        views.ScheduleCreateView.as_view(),
        name="course_schedules-list",
    ),
    path("schedules", views.ScheduleListView.as_view(), name="schedule-list"),
    path("schedule/<int:pk>", views.ScheduleView.as_view(), name="schedule-detail"),
    path("sessions", views.SessionView.as_view(), name="session-list"),
    path("session/<int:pk>", views.SessionView.as_view(), name="session-detail"),
    path("schedule_selector", views.ScheduleSelector.as_view()),
    path("courses", views.CourseView.as_view(), name="course-list"),
]

querypatterns = [
    path(
        "datequery",
        views.DateQuery.as_view(),
    ),
    path("statquery", views.StatQuery.as_view()),
]

urlpatterns = list(userpatterns + modelpatterns + querypatterns)
